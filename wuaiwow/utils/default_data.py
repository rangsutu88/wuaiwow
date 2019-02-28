# coding:utf-8
# import StringIO
# from werkzeug.datastructures import FileStorage

from wuaiwow.utils.modelHelper import (find_or_create_permission, find_or_create_user, 
                                       get_role_by_name, create_role)


def create_all_permissions(permission_config):
    permissions = []
    for idx, role in enumerate(permission_config):
        role_obj = get_role_by_name(role=role[1])
        if not role_obj:
            role_obj = create_role(role=role[1], label=role[2])
        created, ps = find_or_create_permission(value=role[0], need_created=True, role=role_obj)
        permissions.append(ps)
    return permissions


def init_users(permission_config):
    """ init default user """

    perms = create_all_permissions(permission_config)

    #  add default users，
    #  roles, L1=player,L8=GM,L10=admin
    user = find_or_create_user(u'luffy', u'wuaiwow@gmail.com', '123456', perms[-1].value)
    user = find_or_create_user(u'gm', u'825518250@qq.com', '123456', perms[-3].value)
    user = find_or_create_user(u'Zoro', u'it1780@sina.com', '123456', perms[0].value)


def init_news():
    """ init default news """
    pass


def add_default_data(permission_config):
    """ 初始化数据 """
    init_users(permission_config)
    init_news()
