from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    create_engine
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime
import enum
import graphviz

Base = declarative_base()

# ------------------------------------------------------------Add commentMore actions
# Definición de un enum para el tipo de Media (imagen, video, etc.)
class MediaType(enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    GIF = "GIF"
# ------------------------------------------------------------


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)

    # Relaciones
    posts = relationship('Post', backref='user', cascade='all, delete-orphan')
    comments = relationship('Comment', backref='author', cascade='all, delete-orphan')
    media = relationship('Media', backref='owner', cascade='all, delete-orphan')

    # Relaciones de seguidores (auto-relación many-to-many mediante tabla Follower)
    following = relationship(
        'Follower',
        foreign_keys='Follower.user_from_id',
        backref='follower',
        cascade='all, delete-orphan'
    )
    followers = relationship(
        'Follower',
        foreign_keys='Follower.user_to_id',
        backref='followee',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Follower(Base):
    __tablename__ = 'follower'

    id = Column(Integer, primary_key=True)
    user_from_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user_to_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    followed_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Follower(from={self.user_from_id}, to={self.user_to_id})>"


class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    caption = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relaciones
    comments = relationship('Comment', backref='post', cascade='all, delete-orphan')
    media = relationship('Media', backref='post', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Post(id={self.id}, user_id={self.user_id})>"


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    comment_text = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Comment(id={self.id}, author_id={self.author_id}, post_id={self.post_id})>"


class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True)
    type = Column(Enum(MediaType), nullable=False)   # IMAGE, VIDEO, GIF, etc.
    url = Column(String(255), nullable=False)
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Media(id={self.id}, type={self.type}, post_id={self.post_id})>"


# ------------------------------------------------------------
# Función para generar un diagrama del modelo (diagram.png) con estilo tipo QuickDatabaseDiagrams
def _generate_colored_diagram():
    dot = graphviz.Digraph('Instagram_Model', format='png')
    dot.attr(rankdir='LR', splines='ortho', bgcolor='white')

    def create_table_node(name, columns):
        """
        Crea un nodo con etiqueta HTML que imita el estilo de QuickDatabaseDiagrams:
        - Header azul con texto blanco (nombre de la tabla)
        - Filas blanco con nombre de campo y tipo en gris
        - Cada celda de nombre de campo tiene atributo PORT para poder conectar flechas con puertos
        """
        # Fila de encabezado (span 2 columnas)
        header = f'<TR><TD COLSPAN="2" BGCOLOR="deepskyblue" ALIGN="CENTER"><FONT COLOR="white"><B>{name}</B></FONT></TD></TR>'

        # Filas de cuerpo: cada columna dividida en nombre y tipo
        body_rows = ''
        for col in columns:
            field_name, field_type = (x.strip() for x in col.split(':'))
            body_rows += (
                f'<TR>'
                f'<TD PORT="{field_name}" ALIGN="LEFT">{field_name}</TD>'
                f'<TD ALIGN="RIGHT"><FONT COLOR="gray">{field_type}</FONT></TD>'
                f'</TR>'
            )

        # Combinar todo en etiqueta de tabla HTML
        html_label = f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">{header}{body_rows}</TABLE>>'
        dot.node(name, label=html_label, shape='plaintext')

    # Definir cada tabla con sus columnas (nombre: tipo)
    create_table_node('User', [
        'ID: int',
        'username: string',
        'firstname: string',
        'lastname: string',
        'email: string'
    ])

    create_table_node('Follower', [
        'user_from_id: int',
        'user_to_id: int',
        'followed_at: datetime'
    ])

    create_table_node('Post', [
        'ID: int',
        'user_id: int',
        'caption: text',
        'created_at: datetime'
    ])

    create_table_node('Comment', [
        'ID: int',
        'comment_text: string',
        'author_id: int',
        'post_id: int',
        'created_at: datetime'
    ])

    create_table_node('Media', [
        'ID: int',
        'type: enum',
        'url: string',
        'post_id: int',
        'uploaded_at: datetime'
    ])

    # Conexiones entre tablas usando puertos:
    # Follower.user_from_id → User.ID
    dot.edge('Follower:user_from_id', 'User:ID', arrowhead='none')
    # Follower.user_to_id → User.ID
    dot.edge('Follower:user_to_id', 'User:ID', arrowhead='none')
    # Post.user_id → User.ID
    dot.edge('Post:user_id', 'User:ID', arrowhead='none')
    # Comment.author_id → User.ID
    dot.edge('Comment:author_id', 'User:ID', arrowhead='none')
    # Comment.post_id → Post.ID
    dot.edge('Comment:post_id', 'Post:ID', arrowhead='none')
    # Media.post_id → Post.ID
    dot.edge('Media:post_id', 'Post:ID', arrowhead='none')

    # Generar archivo "diagram.png" en la raíz del proyecto
    dot.render(filename='diagram', cleanup=True)
# ------------------------------------------------------------


if __name__ == '__main__':
    # 1. Crear motor de base de datos (SQLite local para este ejemplo)
    engine = create_engine('sqlite:///instagram.db')

    # 2. Crear todas las tablas en la base de datos
    Base.metadata.create_all(engine)

    # 3. Generar el diagrama coloreado como 'diagram.png'
    _generate_colored_diagram()

    print("Tablas creadas y 'diagram.png' generado con estilo QuickDatabaseDiagrams.")