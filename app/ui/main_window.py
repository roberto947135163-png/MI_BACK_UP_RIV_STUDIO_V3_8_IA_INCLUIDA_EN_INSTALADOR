from pathlib import Path
from PySide6.QtCore import Qt, QUrl, QMimeData, QThread, Signal, QTimer, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QDrag, QIcon, QColor
from PySide6.QtWidgets import (QMainWindow,QWidget,QHBoxLayout,QVBoxLayout,QLabel,QPushButton,
 QFileDialog,QTableWidget,QTableWidgetItem,QTableView,QHeaderView,QMessageBox,QLineEdit,QProgressBar,
 QFrame,QAbstractItemView,QDialog,QRadioButton,QButtonGroup,QSpinBox,QDialogButtonBox,QInputDialog,
 QTreeWidget,QTreeWidgetItem,QStackedWidget,QMenu,QColorDialog,QFormLayout,QComboBox,QCheckBox,QApplication,QProgressDialog)
from PySide6.QtMultimedia import QMediaPlayer,QAudioOutput
from app.core.scanner import scan_folder,read_metadata
from app.core.database import upsert_track,all_tracks,update_analysis,mark_analysis_error,pending_analysis
from app.core.organizer import plan_copy,execute_plan

class VirtualMusicModel(QAbstractTableModel):
    """Qt requests only visible cells. No 12,496 x 9 widget allocations."""
    HEADERS = ['Título','Artista','Género','Duración','BPM','Key','Camelot','Energía','Ubicación']
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = []
    def set_tracks(self, rows):
        self.beginResetModel()
        self.rows = rows
        self.endResetModel()
    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)
    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.HEADERS)
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role==Qt.DisplayRole and orientation==Qt.Horizontal:
            return self.HEADERS[section]
        return None
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role not in (Qt.DisplayRole, Qt.ToolTipRole):
            return None
        d=self.rows[index.row()]
        duration=d.get('duration')
        dur=f'{int(duration//60):02d}:{int(duration%60):02d}' if duration else '--:--'
        values=[d.get('title') or d.get('filename') or '', d.get('artist') or 'Desconocido',
                d.get('display_genre') or 'POR CLASIFICAR', dur, d.get('bpm') or '—',
                d.get('musical_key') or '—', d.get('camelot') or '—',
                d.get('energy') if d.get('energy') is not None else '—', d.get('path') or '']
        return str(values[index.column()])
    def path_at(self, row):
        return self.rows[row]['path'] if 0 <= row < len(self.rows) else None

class LibraryLoadWorker(QThread):
    loaded=Signal(list)
    failed=Signal(str)
    def run(self):
        try:
            from app.core.genre_ai import prediction_map
            from app.core.genre_taxonomy import normalize_genre
            from app.core import library_views as lib
            predictions=prediction_map(); overrides=lib.overrides()
            result=[]
            for row in all_tracks():
                d=dict(row);p=d['path']; override=overrides.get(p);pred=predictions.get(p)
                source=override[0] if override else (pred[0] if pred else None)
                main,sub=normalize_genre(source)
                d['display_genre']=main
                d['display_subgenre']=override[1] if override and override[1] and override[1]!='General' else sub
                result.append(d)
            self.loaded.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))

class ScanWorker(QThread):
    found=Signal(dict)
    finished_count=Signal(int)
    def __init__(self,root):
        super().__init__(); self.root=root
    def run(self):
        count=0
        for p in scan_folder(self.root):
            try:
                d=read_metadata(p); upsert_track(d); self.found.emit(d); count+=1
            except Exception:
                continue
        self.finished_count.emit(count)

class AnalysisWorker(QThread):
    progress_count = Signal(int, int, str)
    finished_count = Signal(int, int)
    def __init__(self, paths):
        super().__init__()
        self.paths = paths
        self._stop = False
    def stop(self):
        self._stop = True
    def run(self):
        from app.core.audio_analysis import analyze_audio
        ok = errors = 0
        for index, path in enumerate(self.paths, 1):
            if self._stop:
                break
            try:
                if not Path(path).is_file():
                    raise FileNotFoundError(path)
                result = analyze_audio(path)
                update_analysis(path, result)
                ok += 1
            except Exception as exc:
                mark_analysis_error(path, exc)
                errors += 1
            self.progress_count.emit(index, len(self.paths), Path(path).name)
        self.finished_count.emit(ok, errors)

class GenreWorker(QThread):
    progress_count=Signal(int,int,str)
    completed=Signal(str)
    def __init__(self,mode,paths=None):
        super().__init__(); self.mode=mode; self.paths=paths or []; self._stop=False
    def stop(self): self._stop=True
    def run(self):
        from app.core.genre_ai import train_from_library,save_prediction
        from app.core.pretrained_genre import classify_audio,model_ready
        from app.core.database import APP_DIR
        if self.mode=='train':
            try:
                result=train_from_library()
                self.completed.emit('Modelo local entrenado: '+str(result['genres']))
            except Exception as exc: self.completed.emit('No se pudo entrenar: '+str(exc))
            return
        ok=uncertain=errors=0
        import onnxruntime as ort
        from app.core.pretrained_genre import model_paths
        from app.core.pretrained_genre import active_model_dir
        options=ort.SessionOptions()
        options.intra_op_num_threads=2
        options.inter_op_num_threads=1
        model_path,_=model_paths(active_model_dir())
        try:
            session=ort.InferenceSession(str(model_path),sess_options=options,providers=['CPUExecutionProvider'])
        except Exception as exc:
            self.completed.emit('No se pudo cargar el modelo ONNX: '+str(exc));return
        for index,path in enumerate(self.paths,1):
            if self._stop: break
            try:
                result=classify_audio(path,active_model_dir(),session=session)
                save_prediction(path,result)
                if result['status']=='classified': ok+=1
                else: uncertain+=1
            except Exception: errors+=1
            self.progress_count.emit(index,len(self.paths),Path(path).name)
        self.completed.emit(f'IA ONNX: {ok} asignadas, {uncertain} por clasificar, {errors} errores. Revisa el modelo y los audios si hubo errores.')

class ModelDownloadWorker(QThread):
    progress_bytes = Signal(str, int)
    completed = Signal(str)
    failed = Signal(str)
    def run(self):
        try:
            from app.core.model_install import install_model
            from app.core.database import APP_DIR
            install_model(APP_DIR / 'models', lambda name, count: self.progress_bytes.emit(name, count))
            self.completed.emit('Modelo ONNX descargado. Ya puedes usar IA: Géneros.')
        except Exception as exc:
            self.failed.emit(str(exc))

class AnalysisChoice(QDialog):
    def __init__(self,parent,selected_count,pending_count):
        super().__init__(parent)
        self.setWindowTitle('Elegir alcance del análisis')
        self.resize(450,220)
        layout=QVBoxLayout(self)
        layout.addWidget(QLabel('Elige qué canciones analizar (CPU, sin modificar los archivos):'))
        self.selected=QRadioButton(f'Selección actual ({selected_count})')
        self.batch=QRadioButton('Primeras canciones pendientes (lote)')
        self.all=QRadioButton(f'Todas las pendientes ({pending_count})')
        for w in (self.selected,self.batch,self.all): layout.addWidget(w)
        self.limit=QSpinBox(); self.limit.setRange(1,1000); self.limit.setValue(25)
        layout.addWidget(self.limit)
        self.selected.setEnabled(selected_count>0)
        self.selected.setChecked(selected_count>0)
        if selected_count==0:self.batch.setChecked(True)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    def choice(self):
        return 'selected' if self.selected.isChecked() else 'batch' if self.batch.isChecked() else 'all'

from app.core import library_views as lib

class PlaylistTree(QTreeWidget):
    """Accept file URLs dragged from the library; store virtual references only."""
    def __init__(self,parent=None):
        super().__init__(parent);self.setAcceptDrops(True);self.setDragDropMode(QAbstractItemView.DropOnly)
    def dragEnterEvent(self,event):
        if event.mimeData().hasUrls():event.acceptProposedAction()
        else:super().dragEnterEvent(event)
    def dragMoveEvent(self,event):
        item=self.itemAt(event.position().toPoint())
        if item and item.data(0,Qt.UserRole) and item.data(0,Qt.UserRole)[0]=='playlist' and event.mimeData().hasUrls():event.acceptProposedAction()
        else:event.ignore()
    def dropEvent(self,event):
        item=self.itemAt(event.position().toPoint())
        if not item:return
        data=item.data(0,Qt.UserRole)
        if not data or data[0]!='playlist':return
        paths=[url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
        if paths:
            lib.add_tracks(data[1],paths);event.acceptProposedAction()
            window=self.window()
            if hasattr(window,'status'):window.status.setText(f'{len(paths)} canciones agregadas a playlist (referencias virtuales)')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg=lib.settings();self.page='Inicio';self.active_paths=None;self.clipboard_paths=[]
        self.genre_filter=None;self.folder_id=None;self.all_data=[];self._tracks_loaded=False;self._render_generation=0
        self.player=QMediaPlayer(self);self.audio=QAudioOutput(self);self.player.setAudioOutput(self.audio)
        self.build_ui();self.apply_theme();self.navigate('Inicio')
        QTimer.singleShot(0,self.begin_library_load)

    def apply_theme(self):
        c=self.cfg['accent']
        self.setWindowTitle(f"{self.cfg['app_name']} · {self.cfg['owner']}")
        self.setStyleSheet(f'''QMainWindow,QWidget{{background:#0b0b14;color:#f0eef7;font-family:'Segoe UI'}}
        QLabel#brand{{color:{c};font-size:25px;font-weight:800}}
        QPushButton{{background:#242036;border:1px solid #51426a;border-radius:8px;padding:9px;color:white}}
        QPushButton:hover{{border-color:{c};background:#33264a}}
        QLineEdit,QTreeWidget,QTableWidget{{background:#141320;border:1px solid #3b3450;border-radius:7px;padding:6px}}
        QHeaderView::section{{background:#251e36;color:#e2d2ff;padding:8px;border:0}}
        QProgressBar::chunk{{background:{c}}}''')

    def build_ui(self):
        self.resize(1450,850);self.setMinimumSize(1050,650)
        root=QWidget();self.setCentralWidget(root);outer=QHBoxLayout(root)
        side=QFrame();side.setFixedWidth(185);sv=QVBoxLayout(side)
        brand=QLabel('MI BACK UP');brand.setObjectName('brand');sv.addWidget(brand)
        self.owner_label=QLabel('RIV STUDIO');sv.addWidget(self.owner_label)
        self.nav_buttons={}
        for name in ['Inicio','Todos los temas','Géneros','Playlists','Favoritos','Configuración']:
            b=QPushButton(name);b.clicked.connect(lambda checked=False,page=name:self.navigate(page));sv.addWidget(b);self.nav_buttons[name]=b
        sv.addStretch();sv.addWidget(QLabel('OFFLINE · ARCHIVOS ORIGINALES INTACTOS'));outer.addWidget(side)
        center=QVBoxLayout();top=QHBoxLayout()
        self.title=QLabel('Inicio');self.title.setStyleSheet('font-size:21px;font-weight:700');top.addWidget(self.title);top.addStretch()
        for label,method in [('＋ Analizar disco',self.choose_scan),('Analizar BPM / Key',self.start_analysis),('IA: Géneros',self.ai_genres)]:
            b=QPushButton(label);b.clicked.connect(method);top.addWidget(b)
            if label=='Analizar BPM / Key':self.analysis_button=b
        center.addLayout(top)
        self.search=QLineEdit();self.search.setPlaceholderText('Buscar por nombre de canción, artista o género…')
        self.search.textChanged.connect(self.filter_rows);center.addWidget(self.search)
        self.stack=QStackedWidget();center.addWidget(self.stack,1)
        home=QWidget();hv=QVBoxLayout(home)
        intro=QLabel('MI BACK UP  ·  RIV STUDIO');intro.setStyleSheet('font-size:30px;font-weight:700');hv.addWidget(intro)
        hv.addWidget(QLabel('Escribe el nombre de una canción arriba: los resultados aparecerán inmediatamente.'))
        hv.addStretch();self.stack.addWidget(home)
        self.table=QTableView();self.music_model=VirtualMusicModel(self);self.table.setModel(self.music_model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows);self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers);self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setDefaultSectionSize(135)
        self.table.horizontalHeader().setStretchLastSection(True);self.table.setDragEnabled(True);self.table.setDragDropMode(QAbstractItemView.DragOnly)
        self.table.startDrag=self.start_drag;self.table.doubleClicked.connect(self.play_selected)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu);self.table.customContextMenuRequested.connect(self.context_menu)
        self.stack.addWidget(self.table)
        self.folder_page=QWidget();fl=QHBoxLayout(self.folder_page)
        self.tree=PlaylistTree();self.tree.setHeaderLabel('Carpetas virtuales');self.tree.itemClicked.connect(self.tree_clicked)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu);self.tree.customContextMenuRequested.connect(self.tree_context)
        fl.addWidget(self.tree,1)
        self.folder_table=QTableWidget(0,4);self.folder_table.setHorizontalHeaderLabels(['Título','Artista','Género','Ruta'])
        self.folder_table.setSelectionBehavior(QAbstractItemView.SelectRows);self.folder_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.folder_table.setEditTriggers(QAbstractItemView.NoEditTriggers);self.folder_table.setDragEnabled(True);self.folder_table.setDragDropMode(QAbstractItemView.DragOnly)
        self.folder_table.startDrag=self.start_drag;self.folder_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.folder_table.customContextMenuRequested.connect(self.context_menu)
        fl.addWidget(self.folder_table,3);self.stack.addWidget(self.folder_page)
        self.folder_controls=QHBoxLayout();center.addLayout(self.folder_controls)
        self.create_btn=QPushButton('＋ Crear carpeta');self.create_btn.clicked.connect(self.create_playlist_folder)
        self.folder_controls.addWidget(self.create_btn)
        self.add_btn=QPushButton('Agregar selección a carpeta');self.add_btn.clicked.connect(self.add_selected_to_playlist)
        self.folder_controls.addWidget(self.add_btn)
        self.folder_controls.addStretch()
        self.progress=QProgressBar();self.progress.hide();center.addWidget(self.progress)
        self.status=QLabel('Listo');center.addWidget(self.status)
        right=QFrame();right.setFixedWidth(185);rv=QVBoxLayout(right)
        rv.addWidget(QLabel('REPRODUCTOR'));self.now=QLabel('Ninguna canción seleccionada');self.now.setWordWrap(True);rv.addWidget(self.now)
        for label,fn in [('▶ Reproducir',self.play_selected),('Ⅱ Pausar',self.player.pause),('■ Detener',self.player.stop),('☆ Favorito',self.favorite_selected)]:
            b=QPushButton(label);b.clicked.connect(fn);rv.addWidget(b)
        rv.addWidget(QLabel('Arrastra canciones a VirtualDJ.'))
        rv.addStretch();outer.addLayout(center,1);outer.addWidget(right)

    def begin_library_load(self):
        if getattr(self,"_loading",False): return
        self._loading=True
        self.status.setText("Cargando biblioteca en segundo plano…")
        self.loader=LibraryLoadWorker()
        self.loader.loaded.connect(self.library_loaded)
        self.loader.failed.connect(lambda e:self.status.setText("Error al cargar biblioteca: "+e))
        self.loader.finished.connect(lambda:setattr(self,"_loading",False))
        self.loader.start()

    def library_loaded(self,data):
        self.all_data=data
        self._tracks_loaded=True
        self.navigate(self.page)

    def load_tracks(self, force=False):
        if force:
            self._tracks_loaded=False
            self.begin_library_load()
        # Do not query 12k+ records on the UI thread.

    def navigate(self,page):
        self.page=page;self.title.setText(page);self.load_tracks()
        self.search.setPlaceholderText('Buscar canción por nombre, artista o género…')
        self.create_btn.setVisible(page=='Playlists');self.add_btn.setVisible(page=='Playlists')
        if page=='Configuración':self.show_settings();return
        if page in ('Géneros','Playlists','Favoritos'):
            self.stack.setCurrentIndex(2);self.search.hide();self.populate_tree()
        elif page=='Inicio':
            self.search.show();self.search.clear();self.stack.setCurrentIndex(0)
            self.status.setText(f'Inicio · {len(self.all_data)} canciones registradas · Busca para ver resultados')
        else:
            self.search.show();self.search.clear();self.stack.setCurrentIndex(1)
            self.populate_table(self.all_data)

    def populate_table(self,rows):
        # QTableView paints only the viewport, even with thousands of tracks.
        self.music_model.set_tracks(rows)
        self.status.setText(f'{len(rows)} coincidencias · desplázate con la rueda para ver todas las canciones.')

    def filter_rows(self,term):
        if self.page not in ('Inicio','Todos los temas'):return
        term=term.strip().casefold()
        if self.page=='Inicio' and not term:
            self.stack.setCurrentIndex(0);return
        self.stack.setCurrentIndex(1)
        if not term:matches=self.all_data
        else:matches=[d for d in self.all_data if term in (d.get('title') or d['filename']).casefold() or
            term in (d.get('artist') or '').casefold() or term in d['display_genre'].casefold()]
        self.populate_table(matches)

    def populate_tree(self):
        self.tree.clear();self.folder_table.setRowCount(0)
        if self.page=='Playlists':
            items={None:self.tree.invisibleRootItem()};waiting=lib.folders()
            for _ in range(len(waiting)+1):
                for d in waiting[:]:
                    if d['parent_id'] in items:
                        item=QTreeWidgetItem(items[d['parent_id']],[d['name']]);item.setData(0,Qt.UserRole,('playlist',d['id']))
                        items[d['id']]=item;waiting.remove(d)
            self.status.setText('Crea carpetas y agrega canciones: no se duplican archivos físicos.')
        else:
            if self.page=='Favoritos':allowed=lib.favorites();tracks=[d for d in self.all_data if d['path'] in allowed]
            else:tracks=self.all_data
            groups={}
            for d in tracks:groups.setdefault(d['display_genre'],{}).setdefault(d['display_subgenre'],[]).append(d)
            for genre,subgenres in sorted(groups.items()):
                parent=QTreeWidgetItem(self.tree,[f'{genre} ({sum(map(len,subgenres.values()))})'])
                parent.setData(0,Qt.UserRole,('genre',genre,None))
                for sub,rows in sorted(subgenres.items()):
                    child=QTreeWidgetItem(parent,[f'{sub} ({len(rows)})']);child.setData(0,Qt.UserRole,('genre',genre,sub))
            self.status.setText(f'{len(tracks)} canciones organizadas en carpetas virtuales por género')

    def tree_clicked(self,item,column):
        data=item.data(0,Qt.UserRole)
        if not data:return
        if data[0]=='playlist':
            self.folder_id=data[1];allowed=lib.folder_paths(self.folder_id)
            tracks=[d for d in self.all_data if d['path'] in allowed]
        else:
            self.folder_id=None;genre=data[1];sub=data[2]
            allowed=lib.favorites() if self.page=='Favoritos' else None
            tracks=[d for d in self.all_data if d['display_genre']==genre and (sub is None or d['display_subgenre']==sub)
                    and (allowed is None or d['path'] in allowed)]
        self.folder_table.setRowCount(min(len(tracks),100))
        for i,d in enumerate(tracks[:100]):
            for j,value in enumerate([d.get('title') or d['filename'],d.get('artist') or 'Desconocido',d['display_genre'],d['path']]):
                self.folder_table.setItem(i,j,QTableWidgetItem(str(value)))
        self.status.setText(f'{len(tracks)} canciones en carpeta · mostrando primeras {min(len(tracks),100)}')

    def create_playlist_folder(self):
        parent=self.folder_id if self.page=='Playlists' else None
        name,ok=QInputDialog.getText(self,'Crear carpeta','Nombre de carpeta o set:')
        if ok and name.strip():
            try:lib.create_folder(name,parent);self.populate_tree()
            except Exception as exc:QMessageBox.warning(self,'Carpeta',str(exc))

    def add_selected_to_playlist(self):
        paths=self.selected_paths()
        if not paths:QMessageBox.information(self,'Playlists','Selecciona canciones en Todos los temas y utiliza clic derecho → Agregar a playlist.');return
        self.pick_playlist(paths)

    def pick_playlist(self,paths):
        folders=lib.folders()
        if not folders:
            QMessageBox.information(self,'Playlists','Crea primero una carpeta en Playlists.');return
        labels=[f"{x['name']} (ID {x['id']})" for x in folders]
        label,ok=QInputDialog.getItem(self,'Agregar a playlist','Carpeta:',labels,0,False)
        if ok:
            target=folders[labels.index(label)]['id'];lib.add_tracks(target,paths)
            self.status.setText(f'{len(paths)} referencias agregadas sin copiar los audios')
            if self.page=='Playlists':self.populate_tree()

    def tree_context(self,point):
        item=self.tree.itemAt(point)
        if not item or self.page!='Playlists':return
        data=item.data(0,Qt.UserRole)
        if not data or data[0]!='playlist':return
        menu=QMenu(self);action=menu.addAction('Crear subcarpeta aquí')
        if menu.exec(self.tree.mapToGlobal(point))==action:
            self.folder_id=data[1];self.create_playlist_folder()

    def selected_paths(self):
        if self.stack.currentWidget()==self.folder_page:
            return [self.folder_table.item(i.row(),3).text() for i in self.folder_table.selectionModel().selectedRows()]
        return [self.music_model.path_at(i.row()) for i in self.table.selectionModel().selectedRows() if self.music_model.path_at(i.row())]

    def context_menu(self,point):
        paths=self.selected_paths()
        if not paths:return
        table=self.folder_table if self.stack.currentWidget()==self.folder_page else self.table
        menu=QMenu(self)
        fav=menu.addAction('☆ Agregar / quitar favorito')
        copy=menu.addAction('Copiar referencia')
        paste=menu.addAction('Pegar en carpeta de playlist')
        add=menu.addAction('Agregar a playlist…')
        move=menu.addAction('Mover a otra playlist (solo referencia)')
        genre=menu.addAction('Corregir género / subgénero…')
        action=menu.exec(table.mapToGlobal(point))
        if action==fav:self.favorite_selected()
        elif action==copy:self.clipboard_paths=paths[:];self.status.setText(f'{len(paths)} canciones copiadas al portapapeles interno')
        elif action==paste:
            if self.folder_id is None:QMessageBox.information(self,'Pegar','Selecciona una carpeta de Playlists primero.');return
            lib.add_tracks(self.folder_id,self.clipboard_paths);self.populate_tree()
        elif action==add:self.pick_playlist(paths)
        elif action==move:
            if self.page!='Playlists' or self.folder_id is None:return
            source=self.folder_id;self.pick_playlist(paths);
            if QMessageBox.question(self,'Mover referencia','¿Quitar estas canciones de la playlist original? Los archivos físicos no se moverán.')==QMessageBox.Yes:
                lib.remove_tracks(source,paths)
            self.populate_tree()
        elif action==genre:
            name,ok=QInputDialog.getText(self,'Género','Género principal:')
            if not ok or not name.strip():return
            sub,ok=QInputDialog.getText(self,'Subgénero','Subgénero:',text='General')
            if not ok:return
            for path in paths:lib.genre_override(path,name.strip(),sub.strip() or 'General')
            self.navigate(self.page)

    def favorite_selected(self):
        paths=self.selected_paths()
        if not paths:return
        for path in paths:lib.toggle_favorite(path)
        self.status.setText(f'Favoritos actualizados: {len(paths)} canciones')
        if self.page=='Favoritos':self.populate_tree()

    def start_drag(self,actions):
        paths=[p for p in self.selected_paths() if Path(p).is_file()]
        if not paths:QMessageBox.warning(self,'Disco desconectado','No se encuentran los archivos originales.');return
        source=self.folder_table if self.stack.currentWidget()==self.folder_page else self.table
        mime=QMimeData();mime.setUrls([QUrl.fromLocalFile(p) for p in paths]);drag=QDrag(source);drag.setMimeData(mime);drag.exec(Qt.CopyAction)

    def play_selected(self):
        paths=self.selected_paths()
        if not paths:return
        if not Path(paths[0]).is_file():QMessageBox.warning(self,'Archivo ausente','Conecta el disco externo.');return
        self.player.setSource(QUrl.fromLocalFile(paths[0]));self.player.play();self.now.setText(Path(paths[0]).name)

    def choose_scan(self):
        folder=QFileDialog.getExistingDirectory(self,'Selecciona carpeta musical')
        if not folder:return
        self.progress.setRange(0,0);self.progress.show();self.status.setText('Escaneando…')
        self.worker=ScanWorker(folder)
        self.worker.found.connect(lambda d:self.status.setText('Encontrado: '+d['filename']))
        self.worker.finished_count.connect(self.scan_done);self.worker.start()

    def scan_done(self,count):
        self.progress.hide();self.load_tracks(force=True);self.navigate('Inicio');self.status.setText(f'Escaneo terminado: {count} archivos registrados')

    def start_analysis(self):
        if getattr(self,'analysis_worker',None) and self.analysis_worker.isRunning():
            self.analysis_worker.stop();self.status.setText('Deteniendo después de la canción actual…');return
        pending=set(pending_analysis());selected=[p for p in self.selected_paths() if p in pending]
        dialog=AnalysisChoice(self,len(selected),len(pending))
        if dialog.exec()!=QDialog.Accepted:return
        mode=dialog.choice()
        paths=selected if mode=='selected' else pending_analysis(limit=dialog.limit.value() if mode=='batch' else None)
        if not paths:QMessageBox.information(self,'BPM / Key','No hay canciones pendientes.');return
        if QMessageBox.question(self,'Confirmar',f'Analizar {len(paths)} canciones sin modificar audios originales?')!=QMessageBox.Yes:return
        self.analysis_worker=AnalysisWorker(paths)
        self.analysis_worker.progress_count.connect(self.analysis_progress)
        self.analysis_worker.finished_count.connect(self.analysis_done)
        self.progress.setRange(0,len(paths));self.progress.setValue(0);self.progress.show()
        self.analysis_button.setText('Detener análisis');self.analysis_worker.start()

    def analysis_progress(self,index,total,filename):
        self.progress.setValue(index);self.status.setText(f'{index}/{total}: {filename}')

    def analysis_done(self,ok,errors):
        self.progress.hide();self.analysis_button.setText('Analizar BPM / Key')
        self.navigate(self.page);self.status.setText(f'Análisis: {ok} correctas; {errors} errores')

    def ai_genres(self):
        menu=QMenu(self)
        classify=menu.addAction('Clasificar audio con IA ONNX (selección o lote)')
        info=menu.addAction('Información sobre precisión y licencia')
        action=menu.exec(self.cursor().pos())
        if action==classify:self.classify_genres()
        elif action==info:QMessageBox.information(self,'IA musical',
          'Modelo Discogs-EffNet, licencia CC BY-NC-SA 4.0: solo uso no comercial. '
          'Predice estilos a partir del audio, sin nombres ni etiquetas. No garantiza géneros exactos. '
          'Los archivos originales nunca se mueven. El modelo viene con el instalador.')

    def install_genre_model(self):
        if getattr(self,'model_downloader',None) and self.model_downloader.isRunning():
            QMessageBox.information(self,'Descarga','La descarga ya está en curso.');return
        from app.core.database import APP_DIR
        from app.core.pretrained_genre import model_ready
        if model_ready(APP_DIR/'models'):
            QMessageBox.information(self,'IA instalada','El modelo ONNX ya está instalado.');return
        if QMessageBox.question(self,'Licencia de uso personal',
            'Los pesos de Discogs-EffNet tienen licencia CC BY-NC-SA 4.0. '
            '¿Confirmas que los utilizarás únicamente para fines personales no comerciales y deseas descargarlos desde Essentia?') != QMessageBox.Yes:return
        self.model_downloader=ModelDownloadWorker()
        self.model_downloader.progress_bytes.connect(lambda name,n: self.status.setText(f'Descargando IA: {name} ({n//1048576} MB)'))
        self.model_downloader.completed.connect(lambda msg: (self.status.setText(msg),QMessageBox.information(self,'IA instalada',msg)))
        self.model_downloader.failed.connect(lambda msg: (self.status.setText('Error al descargar IA'),QMessageBox.warning(self,'Descarga fallida',msg)))
        self.model_downloader.start()

    def train_genre(self):
        if getattr(self,'genre_worker',None) and self.genre_worker.isRunning():return
        if QMessageBox.question(self,'Entrenar IA','Se utilizarán canciones etiquetadas como ejemplos. Puede tardar. ¿Continuar?')!=QMessageBox.Yes:return
        self.genre_worker=GenreWorker('train');self.genre_worker.completed.connect(lambda msg:QMessageBox.information(self,'IA local',msg))
        self.genre_worker.start();self.status.setText('Entrenando modelo offline…')

    def classify_genres(self):
        if getattr(self,'genre_worker',None) and self.genre_worker.isRunning():
            self.genre_worker.stop();return
        from app.core.pretrained_genre import model_ready, active_model_dir
        if not model_ready(active_model_dir()):
            QMessageBox.warning(self,'Modelo ONNX ausente','Este instalador no contiene el modelo ONNX. Revisa el resultado de GitHub Actions y vuelve a compilar.');return
        selected=self.selected_paths()
        options=['Selección actual','Primer lote de 25 canciones','Primer lote de 100 canciones']
        choice,ok=QInputDialog.getItem(self,'IA · Alcance','Analizar:',options,0,False)
        if not ok:return
        from app.core.genre_ai import prediction_map
        known=set(prediction_map());paths=selected if choice==options[0] else [d['path'] for d in self.all_data if d['path'] not in known][:25 if choice==options[1] else 100]
        if not paths:QMessageBox.information(self,'IA','No hay canciones seleccionadas o pendientes.');return
        self.genre_worker=GenreWorker('predict',paths)
        self.genre_worker.progress_count.connect(self.analysis_progress)
        self.genre_worker.completed.connect(self.genre_done)
        self.progress.setRange(0,len(paths));self.progress.setValue(0);self.progress.show();self.genre_worker.start()

    def genre_done(self,message):
        self.progress.hide();self.load_tracks(force=True);self.status.setText(message)
        QMessageBox.information(self,'IA local',message)

    def show_settings(self):
        dialog=QDialog(self);dialog.setWindowTitle('Configuración · MI BACK UP');form=QFormLayout(dialog)
        name=QLineEdit(self.cfg['app_name']);form.addRow('Nombre de la aplicación:',name)
        owner=QLineEdit(self.cfg['owner']);form.addRow('Propietario:',owner)
        color=QPushButton('Elegir color');form.addRow('Color principal:',color)
        chosen=[self.cfg['accent']]
        def choose():
            c=QColorDialog.getColor(QColor(chosen[0]),dialog)
            if c.isValid():chosen[0]=c.name();color.setStyleSheet(f'background:{c.name()}')
        color.clicked.connect(choose)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);form.addRow(buttons)
        if dialog.exec()==QDialog.Accepted:
            self.cfg.update({'app_name':name.text().strip() or 'MI BACK UP','owner':owner.text().strip() or 'RIV STUDIO','accent':chosen[0]})
            lib.save_settings(self.cfg);self.apply_theme();self.owner_label.setText(self.cfg['owner'])
        self.navigate('Inicio')

    def closeEvent(self,event):
        super().closeEvent(event)
