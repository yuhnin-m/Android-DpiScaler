from PySide6.QtWidgets import (
    QWidget, QLabel,QVBoxLayout,QFrame
)

def wrap_with_frame(widget: QWidget, object_name: str, title: str = "") -> QFrame:
    container = QFrame()
    container.setObjectName(object_name)
    container.setFrameShape(QFrame.StyledPanel)
    container.setStyleSheet(f"""
        #{object_name} {{
            border: 1px solid #aaa;
            border-radius: 8px;
            padding: 8px;
        }}
    """)
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)
    if title:
        label = QLabel(f"<b>{title}</b>")
        layout.addWidget(label)
    layout.addWidget(widget)
    container.setLayout(layout)
    return container