from datetime import datetime

from sqlalchemy import UniqueConstraint, Index, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.news import News
from models.users import User


class Base(DeclarativeBase):
    pass

class Favorite(Base):
    """
    收藏表ORM模型
    """
    __tablename__ = "favorite"

    __table_args__ = (
        UniqueConstraint("user_id", "news_id", name="user_news_unique"),  # 唯一约束。当前新闻只能收藏1次
        Index("fk_favorite_user_idx", "user_id"),
        Index("fk_favorite_news_idx", "news_id")
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id, ondelete="CASCADE", onupdate="CASCADE"),
                                         nullable=False, comment="用户ID")
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey(News.id, ondelete="CASCADE", onupdate="CASCADE"),
                                         nullable=False, comment="新闻ID")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False,
                                                 comment="收藏时间")

    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, news_id={self.news_id}, created_at={self.created_at})>"