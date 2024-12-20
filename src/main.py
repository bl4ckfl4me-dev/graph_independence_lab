from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QSizePolicy, QWidget,
    QLabel, QInputDialog, QGridLayout, QMessageBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import independence_graph
import random
import sys
import math


class GraphApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Число независимости графа')
        self.setGeometry(100, 100, 600, 500)

        self.nodes = []  # List to store nodes
        self.edges = []  # List to store edges
        self.independent_node_names = []
        self.node_positions = {}
        self.canvas_size = 400
        self.min_distance = 50
        self.dragging_node = None
        self.dragging_offset = (0, 0)

        self.initUI()

    def initUI(self):
        main_layout = QGridLayout()

        self.label = QLabel('Создайте граф и найдите число независимости')
        self.label.setStyleSheet('font-size: 16px;')
        self.label.setMaximumHeight(50)
        main_layout.addWidget(self.label, 0, 0, 1, 2)

        # Creating buttons
        self.add_node_button = self.create_button('Добавить вершину', '#4CAF50', '#388E3C ')
        self.add_node_button.clicked.connect(self.add_node)
        main_layout.addWidget(self.add_node_button, 1, 0)

        self.add_edge_button = self.create_button('Добавить ребро', '#2196F3', '#1976D2')
        self.add_edge_button.clicked.connect(self.add_edge)
        main_layout.addWidget(self.add_edge_button, 2, 0)

        self.remove_node_button = self.create_button('Удалить вершину', '#F44336', '#D32F2F')
        self.remove_node_button.clicked.connect(self.remove_node)
        main_layout.addWidget(self.remove_node_button, 3, 0)

        self.user_info_btn = self.create_button('Информация для пользователя', '#FF9800', '#FB8C00')
        self.user_info_btn.clicked.connect(self.show_user_info_window)
        self.user_info_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        main_layout.addWidget(self.user_info_btn, 1, 1, 2, 1)

        self.result_label = QLabel('Число независимости:')
        self.result_label.setStyleSheet('font-size: 16px;')
        main_layout.addWidget(self.result_label, 3, 1)

        # Canvas for the graph
        self.canvas = FigureCanvas(plt.Figure(figsize=(5, 4)))
        main_layout.addWidget(self.canvas, 4, 0, 1, 2)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def create_button(self, text, background_color=None, background_color_hover=None):
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {background_color if background_color else '#4CAF50'}; /* Зеленый фон */
                color: white; /* Белый текст */
                padding: 10px; /* Отступы */
                border: none; /* Без рамки */
                border-radius: 5px; /* Закругленные углы */
                font-size: 16px; /* Размер шрифта */
            }}
            QPushButton:hover {{
                background-color: {background_color_hover if background_color_hover else '#45a049'}; /* Более темный зеленый при наведении */
            }}
        """)
        return button

    def on_press(self, event):
        if event.inaxes is None:
            return
        for node, (x, y) in self.node_positions.items():
            if (event.xdata - x) ** 2 + (event.ydata - y) ** 2 < (self.min_distance / 2) ** 2:
                self.dragging_node = node
                self.dragging_offset = (x - event.xdata, y - event.ydata)
                break

    def on_release(self, event):
        self.dragging_node = None

    def on_motion(self, event):
        if self.dragging_node is not None and event.inaxes is not None:
            new_x = event.xdata + self.dragging_offset[0]
            new_y = event.ydata + self.dragging_offset[1]
            self.node_positions[self.dragging_node] = (new_x, new_y)
            self.draw_graph()

    def show_user_info_window(self):
        QMessageBox.information(
            self, 'Описание программы',
            'Основной задачей данной программы была реализация '
            'UI-интерфейса для взаимодействия с алгоритмом нахождения числа независимости графа. '
            'В качестве реализации поставленной задачи был выбран язык программирования '
            'Python версии 3.12.7 (в частности был использован фреймворк PyQt с сопутствующими ему библиотеками).\n\n'
            'Реализованный функционал:\n'
            '- Добавление вершины графа\n'
            '- Удаление вершины графа\n'
            '- Добавление грани\n'
            '- Автоматический подсчет числа независимости графа\n'
            '- Графическое выделение независимых вершин графа\n'
            '- Возможность перетаскивания вершин графа по полю'
        )

    def add_node(self):
        node, ok = QInputDialog.getText(self, 'Добавить вершину', 'Введите имя вершины:')
        if ok and node and node not in self.nodes:
            x, y = self.generate_random_position()
            self.nodes.append(node)
            self.node_positions[node] = (x, y)
            self.draw_graph()
        self.find_independence_number()

    def add_edge(self):
        node1, ok1 = QInputDialog.getText(self, 'Добавить ребро', 'Введите первую вершину:')
        node2, ok2 = QInputDialog.getText(self, 'Добавить ребро', 'Введите вторую вершину:')
        if ok1 and ok2 and node1 in self.nodes and node2 in self.nodes:
            self.edges.append((node1, node2))
            self.draw_graph()
        self.find_independence_number()

    def remove_node(self):
        node, ok = QInputDialog.getText(self, 'Удалить вершину', 'Введите имя вершины для удаления:')
        if ok and node in self.nodes:
            self.nodes.remove(node)
            self.edges = [edge for edge in self.edges if node not in edge]  # Remove edges associated with the node
            del self.node_positions[node]
            self.draw_graph()
        self.find_independence_number()

    def find_independence_number(self):
        # Prepare the adjacency matrix for the C++ function
        adjacency_matrix = [[0] * len(self.nodes) for _ in range(len(self.nodes))]
        for node1, node2 in self.edges:
            idx1 = self.nodes.index(node1)
            idx2 = self.nodes.index(node2)
            adjacency_matrix[idx1][idx2] = 1
            adjacency_matrix[idx2][idx1] = 1  # Undirected graph

        # Get independence number from C++ function
        independent_nodes_idx = independence_graph.get_independence_graph_vertices(adjacency_matrix)
        self.independent_node_names = [name for i, name in enumerate(self.nodes) if i in independent_nodes_idx]
        self.draw_graph()
        self.result_label.setText(f'Число независимости: {len(independent_nodes_idx)}')

    def generate_random_position(self):
        while True:
            x = random.randint(0, self.canvas_size)
            y = random.randint(0, self.canvas_size)
            if self.is_position_valid(x, y):
                return x, y

    def is_position_valid(self, x, y):
        for pos in self.node_positions.values():
            existing_x, existing_y = pos
            distance = math.sqrt((existing_x - x) ** 2 + (existing_y - y) ** 2)
            if distance < self.min_distance:
                return False
        return True

    def draw_graph(self):
        self.canvas.figure.clear()
        if not self.node_positions:
            self.canvas.draw()
            return

        ax = self.canvas.figure.add_subplot(111)

        # Draw edges first so nodes can be on top
        for (node1, node2) in self.edges:
            x_values = [self.node_positions[node1][0], self.node_positions[node2][0]]
            y_values = [self.node_positions[node1][1], self.node_positions[node2][1]]
            ax.plot(x_values, y_values, 'k-')

        # Draw nodes
        independent_nodes = []
        regular_nodes = []
        for name in self.node_positions:
            if name in self.independent_node_names:
                independent_nodes.append(self.node_positions[name])
            else:
                regular_nodes.append(self.node_positions[name])

        if independent_nodes:
            ax.scatter(*zip(*independent_nodes), s=500, c='#FF9800', alpha=1, edgecolors='black', zorder=100)
        if regular_nodes:
            ax.scatter(*zip(*regular_nodes), s=500, c='#2196F3', alpha=1, edgecolors='black', zorder=100)


        # Draw node labels on top
        for node, (x, y) in self.node_positions.items():
            ax.text(x, y, node, fontsize=12, ha='center', va='center', zorder=100)

        ax.axis('off')  # This hides the axes
        ax.set_xlim(-10, self.canvas_size + 10)
        ax.set_ylim(-10, self.canvas_size + 10)
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GraphApp()
    window.show()
    sys.exit(app.exec_())
