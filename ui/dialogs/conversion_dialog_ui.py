# ui/dialogs/conversion_dialog_ui.py

from .auto_spinbox import AutoSpinBox
from ui.qt_compat import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QHBoxLayout,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QCheckBox,
    QLabel,
    QStackedWidget,
    QGraphicsView,
    QGraphicsScene,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QGridLayout,
    QSplitter,
    QSizePolicy,
    QFont,
    QPainter,
    Qt,
    QTimer
)

class ConversionDialogUI:
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(0)
        main_splitter.setChildrenCollapsible(False)

        # Left panel
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)

        # Right panel
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)

        main_splitter.setSizes([516, 318])
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)
        main_splitter.handle(1).setEnabled(False)

        layout.addWidget(main_splitter)

        self.load_input_image()
        self.on_output_size_changed()
        self.on_bpp_changed()

    def create_left_panel(self):
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_layout.setContentsMargins(0, 0, 0, 0)

        input_header = QLabel(self._tr("conv_input_image"))
        input_header.setFont(QFont("Arial", 10, QFont.Bold))
        input_header.setStyleSheet("QLabel { background: #555; color: white; padding: 4px; border-radius: 4px; }")
        input_header.setFixedSize(512, 30)
        left_layout.addWidget(input_header)

        self.input_view = QGraphicsView()
        self.input_scene = QGraphicsScene()
        self.input_view.setScene(self.input_scene)
        self.input_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.input_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: 1px solid #ccc; }")
        self.input_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.input_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.input_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.input_view.setFixedSize(514, 514)
        left_layout.addWidget(self.input_view)

        return left_panel

    def create_right_panel(self):
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        right_layout.setContentsMargins(0, 0, 0, 0)

        params_group = QGroupBox(self._tr("conv_conversion_params"))
        form_layout = QFormLayout()

        self.create_mode_selector(form_layout)
        self.create_bpp_selector(form_layout)
        self.create_palette_selector(form_layout)
        self.create_8bpp_params(form_layout)
        self.create_general_params(form_layout)
        self.create_output_size(form_layout)

        params_group.setLayout(form_layout)
        params_group.setFixedWidth(366)
        right_layout.addWidget(params_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat(self._tr("conv_ready"))
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)

        right_layout.addStretch()

        self.create_buttons(right_layout)

        return right_panel

    def create_mode_selector(self, form_layout):
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([self._tr("conv_text_mode"), self._tr("conv_rot_mode")])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        form_layout.addRow(self._tr("conv_bg_mode"), self.mode_combo)

    def create_bpp_selector(self, form_layout):
        self.bpp_combo = QComboBox()
        self.bpp_combo.addItems([self._tr("bpp_4bpp"), self._tr("bpp_8bpp")])
        self.bpp_combo.setCurrentIndex(0)
        self.bpp_combo.currentIndexChanged.connect(self.on_bpp_changed)
        form_layout.addRow(self._tr("conv_bpp"), self.bpp_combo)

    def create_palette_selector(self, form_layout):
        self.palettes_container = QWidget()
        palettes_main_layout = QVBoxLayout()
        palettes_main_layout.setContentsMargins(0, 0, 0, 0)
        palettes_main_layout.setSpacing(1)
        self.palettes_container.setLayout(palettes_main_layout)

        self.palette_tilemap_radio_container = QWidget()
        radio_layout = QHBoxLayout()
        radio_layout.setContentsMargins(0, 0, 0, 0)

        self.use_palettes_radio = QRadioButton(self._tr("conv_use_palettes"))
        self.use_tilemap_radio = QRadioButton(self._tr("conv_use_tilemap"))
        self.use_palettes_radio.setChecked(True)
        self.use_palettes_radio.toggled.connect(self.on_palette_tilemap_toggled)

        radio_layout.addWidget(self.use_palettes_radio)
        radio_layout.addWidget(self.use_tilemap_radio)
        self.palette_tilemap_radio_container.setLayout(radio_layout)
        palettes_main_layout.addWidget(self.palette_tilemap_radio_container)

        self.palettes_widget_container = QWidget()
        palettes_inner_layout = QVBoxLayout()
        palettes_inner_layout.setContentsMargins(0, 0, 0, 0)

        self.palettes_widget = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(6)
        self.palettes_widget.setLayout(grid_layout)

        self.palette_checks = []
        for i in range(16):
            cb = QCheckBox("")
            cb.setFixedSize(16, 16)
            cb.setChecked(i == 0)
            cb.toggled.connect(self.on_palette_toggled)
            self.palette_checks.append(cb)
            grid_layout.addWidget(cb, 0, i)

            label = QLabel(hex(i)[2:].upper())
            label.setFixedSize(16, 12)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("QLabel { font-size: 10px; font-weight: bold; color: #555; margin: 0; padding: 0; }")
            grid_layout.addWidget(label, 1, i)

        self.palettes_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.palettes_widget.setFixedWidth(300)
        palettes_inner_layout.addWidget(self.palettes_widget)
        self.palettes_widget_container.setLayout(palettes_inner_layout)
        palettes_main_layout.addWidget(self.palettes_widget_container)

        self.tilemap_file_container = QWidget()
        tilemap_layout = QFormLayout()
        tilemap_layout.setContentsMargins(0, 0, 0, 5)

        file_layout = QHBoxLayout()
        file_layout.setContentsMargins(0, 0, 0, 0)

        self.tilemap_path_edit = QLineEdit()
        self.tilemap_path_edit.setPlaceholderText(self._tr("conv_select_bin"))
        self.tilemap_path_edit.setReadOnly(True)

        self.tilemap_browse_btn = QPushButton(self._tr("conv_browse"))
        self.tilemap_browse_btn.clicked.connect(self.browse_tilemap_file)

        file_layout.addWidget(self.tilemap_path_edit)
        file_layout.addWidget(self.tilemap_browse_btn)

        file_widget = QWidget()
        file_widget.setLayout(file_layout)
        tilemap_layout.addRow(self._tr("conv_tilemap_file"), file_widget)

        self.tilemap_file_container.setLayout(tilemap_layout)
        self.tilemap_file_container.setVisible(False)
        palettes_main_layout.addWidget(self.tilemap_file_container)

        form_layout.addRow(self.palettes_container)

    def create_8bpp_params(self, form_layout):
        self.start_index = QSpinBox()
        self.start_index.setRange(0, 255)
        self.start_index.setValue(0)
        self.start_index.setVisible(False)

        self.palette_size = AutoSpinBox()
        self.palette_size.setVisible(False)

        form_layout.addRow(self._tr("conv_palette_start"), self.start_index)
        form_layout.addRow(self._tr("conv_palette_size"), self.palette_size)

        self.bpp8_widgets = [self.start_index, self.palette_size]
        self.bpp8_labels = []

        for row_index in [form_layout.rowCount() - 2, form_layout.rowCount() - 1]:
            item = form_layout.itemAt(row_index, QFormLayout.LabelRole)
            if item and item.widget():
                self.bpp8_labels.append(item.widget())
                item.widget().setVisible(False)

        self.palette_size.set_dialog(self)
        self.start_index.valueChanged.connect(self._handle_start_index_change)
        self.palette_size.valueChanged.connect(self.update_8bpp_size)

    def create_general_params(self, form_layout):
        tc_layout = QHBoxLayout()
        tc_layout.setContentsMargins(0, 0, 0, 0)
        tc_layout.setSpacing(4)
        self.transparent_color = QLineEdit("0,0,0")
        self.transparent_color.setPlaceholderText("R,G,B (0-255)")
        self.transparent_color.textChanged.connect(self._update_preview_crop)
        self.eyedropper_btn = QPushButton("🔍")
        self.eyedropper_btn.setFixedSize(24, 24)
        self.eyedropper_btn.setCheckable(True)
        self.eyedropper_btn.setToolTip(self._tr("conv_pick_color"))
        self.eyedropper_btn.setStyleSheet(
            "QPushButton { font-size: 12px; padding: 0; }"
            "QPushButton:checked { background: #aad4f5; border: 1px solid #3399cc; }"
        )
        self.eyedropper_btn.toggled.connect(self.on_eyedropper_toggled)
        tc_layout.addWidget(self.transparent_color)
        tc_layout.addWidget(self.eyedropper_btn)
        tc_widget = QWidget()
        tc_widget.setLayout(tc_layout)
        form_layout.addRow(self._tr("conv_transparent_color"), tc_widget)

        self.extra_transparent = QSpinBox()
        self.extra_transparent.setRange(0, 10)
        self.extra_transparent.setValue(0)
        form_layout.addRow(self._tr("conv_extra_transparent"), self.extra_transparent)

        self.tileset_width = QSpinBox()
        self.tileset_width.setRange(0, 64)
        self.tileset_width.setValue(0)
        self.tileset_width.setSpecialValueText("Auto")
        form_layout.addRow(self._tr("conv_tileset_width"), self.tileset_width)

        self.origin = QLineEdit("0,0")
        self.origin.setPlaceholderText(self._tr("conv_placeholder_origin"))
        form_layout.addRow(self._tr("conv_origin"), self.origin)

    def create_output_size(self, form_layout):
        output_hlayout = QHBoxLayout()
        self.output_combo = QComboBox()
        for key in self.PRESETS.keys():
            self.output_combo.addItem(self._tr(key), key)
        self.output_combo.currentTextChanged.connect(self.on_output_size_changed)
        output_hlayout.addWidget(self.output_combo)
        form_layout.addRow(self._tr("conv_output_size"), output_hlayout)

        self.custom_stack = QStackedWidget()
        self.custom_none = QWidget()
        self.custom_widget = QWidget()
        self.custom_stack.addWidget(self.custom_none)
        self.custom_stack.addWidget(self.custom_widget)

        custom_layout = QFormLayout()
        self.custom_width = QSpinBox()
        self.custom_width.setRange(1, 64)
        self.custom_width.setValue(32)
        self.custom_width.valueChanged.connect(self.update_output_info)
        self.custom_height = QSpinBox()
        self.custom_height.setRange(1, 256)
        self.custom_height.setValue(20)
        self.custom_height.valueChanged.connect(self.update_output_info)
        custom_layout.addRow(self._tr("conv_width_tiles"), self.custom_width)
        custom_layout.addRow(self._tr("conv_height_tiles"), self.custom_height)
        self.custom_widget.setLayout(custom_layout)
        form_layout.addRow(self.custom_stack)

        self.output_info = QLabel(self._tr("conv_output_info", w=256, h=160))
        self.output_info.setStyleSheet("QLabel { font-weight: bold; color: #0066cc; padding: 4px; }")
        form_layout.addRow(self.output_info)

    def create_buttons(self, right_layout):
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton(self._tr("conv_cancel"))
        self.convert_btn = QPushButton(self._tr("conv_convert"))
        self.convert_btn.setDefault(True)

        cancel_btn.clicked.connect(self.reject)
        self.convert_btn.clicked.connect(self.on_convert)

        button_layout.addWidget(self.convert_btn)
        button_layout.addWidget(cancel_btn)

        right_layout.addLayout(button_layout)
