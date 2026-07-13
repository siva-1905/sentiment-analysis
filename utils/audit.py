from flask import request

from extensions import db

from database.models import AuditLog


def create_log(user_id, activity):

    log = AuditLog(

        user_id=user_id,

        activity=activity,

        ip_address=request.remote_addr,

        browser=request.user_agent.string

    )

    db.session.add(log)

    db.session.commit()