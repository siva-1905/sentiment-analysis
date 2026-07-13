from database.models import Notification
from extensions import db


def create_notification(
    user_id,
    title,
    message
):

    notification = Notification(

        user_id=user_id,

        title=title,

        message=message

    )

    db.session.add(notification)

    db.session.commit()