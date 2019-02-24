# -*- coding: utf-8 -*-
import jsonpickle
def userInfo(request):
    user = request.session.get('user','')
    if user:
        return {'user':jsonpickle.loads(user)}
    return {'user':''}