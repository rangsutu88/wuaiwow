# coding:utf-8
from flask import render_template, Blueprint, request, jsonify, url_for
from werkzeug.local import LocalProxy
from flask_user import current_user, login_required
from wuaiwow import db, app, tasks
from wuaiwow.utils import add_blueprint, save_file_upload
from wuaiwow.utils.templateHelper import all_prompt
from wuaiwow.utils.accountHelper import role_required
from wuaiwow.utils.modelHelper import (find_or_create_sidebar, get_permission_by_value,
                                       find_or_create_permission, get_all_roles,
                                       get_role_by_name, get_permission_by_id,
                                       get_less_permission, get_permission_num,
                                       permission_value_by_level, add_role_to_permission,
                                       create_role)
from wuaiwow.models import (Donate, LevelPrompt, AlivePrompt, RacePrompt, Agreement,
                            JobPrompt, GenderPrompt, MoneyPrompt, Sidebar, Permission)

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/add-donate', methods=['GET', 'POST'])
@login_required
@role_required('UPGRADE')
def add_donate():
    result_info = ''
    if request.method == 'POST':
        donate_info = request.form['donateinfotext']
        donate = Donate(info=donate_info)
        try:
            db.session.add(donate)
            db.session.commit()
        except Exception, e:
            result_info = u'更新失败,再试下'
        else:
            result_info = u'更新成功'
    else:
        donate = Donate.query.order_by(Donate.date.desc()).first()
        donate_info = donate.info if donate else " "

    return render_template('custom/cms/admin_add_donate.html',
                           adddonate='class=active',
                           donate_info=donate_info,
                           result=result_info)


@bp.route('/add-userAgreement', methods=['GET', 'POST'])
@login_required
@role_required('UPGRADE')
def add_user_agreement():
    result_info = ''
    if request.method == 'POST':
        content = request.form['agreement-content']
        donate = Agreement(content=content)
        try:
            db.session.add(donate)
            db.session.commit()
        except Exception, e:
            result_info = u'更新失败,再试下'
        else:
            result_info = u'更新成功'
    else:
        agreement = Agreement.query.order_by(Agreement.update.desc()).limit(5).first()
        content = agreement.content if agreement else " "

    return render_template('custom/cms/admin_add_userAgreement.html',
                           adduseragreement='class=active',
                           content=content,
                           result=result_info)


@bp.route('/add-prompt', methods=[])
@login_required
@role_required('UPGRADE')
def add_prompt():
    if request.method == 'POST':
        form = request.get_json()
        try:
            for m in [AlivePrompt, LevelPrompt, RacePrompt, JobPrompt, GenderPrompt, MoneyPrompt]:
                if form['id'] and form['id'] == m.class_id():
                    if form['id'] == 'alive':
                        inst = m(prompt=form['value'], alive= (form['type'] == '1') )
                    else:
                        inst = m(prompt=form['value'])
                    db.session.add(inst)
                    db.session.commit()
                    result = {'status': 'Ok', 'msg': u'添加成功', 'value': form['value']}
                    break
            else:
                result = {'status': 'Err', 'msg': u'添加提示语类型错误'}
        except Exception, e:
                result = {'status': 'Err', 'msg': u'未知错误'}
        return jsonify(result)
    else:
        rst = []
        for m in [AlivePrompt, LevelPrompt, RacePrompt, JobPrompt, GenderPrompt, MoneyPrompt]:
            prompt = all_prompt(m)
            prompt_dict = {'id': m.class_id(), 'title': m.title(), 'prompt': enumerate(prompt)}
            rst.append(prompt_dict)
        return render_template('custom/cms/admin_add_prompt.html',
                               prompts=rst,
                               addprompt='class=active')


@bp.route('/del-prompt', methods=[])
@login_required
@role_required('UPGRADE')
def del_prompt():
    if request.method == 'POST':
        form = request.get_json()
        try:
            for m in [AlivePrompt, LevelPrompt, RacePrompt, JobPrompt, GenderPrompt, MoneyPrompt]:
                if form['id'] and form['id'] == m.class_id():
                    inst = m.query.filter_by(prompt=form['value']).first()
                    if inst:
                        db.session.delete(inst)
                        db.session.commit()
                        result = {'status': 'Ok', 'msg': u'删除成功'}
                    else:
                        result = {'status': 'Err', 'msg': u'提示语不存在'}
                    break
            else:
                result = {'status': 'Err', 'msg': u'要删除的提示语类型错误'}
        except Exception,e:
            result = {'status': 'Err', 'msg': u'未知错误'}
    else:
        result = {'status': 'Err', 'msg': u'请求类型错误'}

    return jsonify(result)


@bp.route('/add-sidebar', methods=['GET', 'POST'])
@login_required
@role_required('UPGRADE')
def add_sidebar():
    default_url = url_for('static', filename='images/default_title.jpg')
    sidebars = [sd.name for sd in Sidebar.query.order_by(Sidebar.created.asc()).all()]
    if request.method == 'POST':
        if request.form['sidebar-name']:
            sd = find_or_create_sidebar(request.form['sidebar-name'])
            if request.files and request.files['sidebar-photo']:
                f = request.files['sidebar-photo']
                try:
                    file_name = save_file_upload(f, app.config['ALLOWED_EXTENSIONS'], app.static_folder)
                    photo_url = url_for('static', filename=file_name)
                except Exception, e:
                    photo_url = default_url
            else:
                photo_url = default_url

            if not sd.image_url or photo_url != default_url:
                sd.image_url = photo_url
            sd.content = request.form['sidebar-content']
            db.session.add(sd)
            db.session.commit()

            sidebars.insert(0, sd.name)
            sidebars.insert(0, u"选择侧边栏编辑或新建侧边栏" if sidebars else u"还未添加侧边栏")
            result = {'status': 'Ok', 'msg': u'添加成功', 'photo_url': sd.image_url, 'titles': sidebars}
        else:
            result = {'status': 'Err', 'msg': u'名称不能为空', 'photo_url': default_url}
        return jsonify(result)
    else:
        photo_url = default_url

    sidebars.insert(0, u"选择侧边栏编辑或新建侧边栏" if sidebars else u"还未添加侧边栏")

    return render_template('custom/cms/admin_add_sidebar.html',
                           addsidebar='class=active',
                           sidebars=enumerate(sidebars),
                           photo=photo_url)


@bp.route('/get-a-sidebar', methods=['GET'])
@login_required
@role_required('UPGRADE')
def get_a_sidebar():
    sd_id = request.args.get('id', '')
    sds = Sidebar.query.order_by(Sidebar.created.desc()).all()
    selected = sds[int(sd_id)-1] if len(sds) >= int(sd_id) else None
    if selected:
        result = {'status': 'Ok', 'msg': u'OK', 'sidebar_name': selected.name,
                  'sidebar_content': selected.content, 'sidebar_photo': selected.image_url}
    else:
        result = {'status': 'Err', 'msg': u'此侧边栏不存在'}
    return jsonify(result)


@bp.route('/change-role-permission/', methods=['GET', 'POST'])
@login_required
@role_required('UPGRADE')
def change_role_permission():
    if request.method == 'POST':
        value = request.form.get('value', None)
        role_permission = request.form.get('newRolePerm', "")
        if not value or value <= 0 or not role_permission:
            result = {'status': 'Err', 'msg': u'参数错误'}
        else:
            command_list = []
            role_perm = [a.split('=') for a in role_permission.split('&')]
            form_value = filter(lambda x: x[0] == 'value', role_perm)[0]
            if not form_value[-1] == value:
                result = {'status': 'Err', 'msg': u'参数错误'}
            else:
                current_permission = get_permission_by_value(value)
                for r, v in role_perm:
                    if r == 'role':
                        role = get_role_by_name(role=v)
                        added, _ = add_role_to_permission(ps=current_permission, role=role)  # 更新权限拥有的role
                        if added:
                            command_list.append((current_permission.value, role.role, role.label))  # 保存更改成功的记录
                else:
                    db.session.commit()
                    result = {'status': 'Ok', 'msg': u'修改成功'}

                # if len(command_list) > 0:
                #     # 更新game server端的对应表
                #     tasks.update_permission_table(command_list)

        return jsonify(result)
    else:
        current_permission = current_user.permission
        roles = set((pr.role for pr in current_permission.roles)) | set(get_all_roles())   # 只显示当前用户拥有的角色及所有非admin角色(并不被当前用户拥有)
        roles = list(roles)
        less_ps = get_less_permission(value=current_permission.value)
        i = 0
        less_roles = []
        role_size = len(roles)
        while 1:
            less_roles.append(roles[i:i+6])
            if i+6 >= role_size:
                break
            else:
                i += 6
        return render_template('custom/cms/admin_permission.html',
                               roles=less_roles,
                               permissions=less_ps,
                               addpermission='class=active')


@bp.route('/add-permission/', methods=['GET', ])
@login_required
@role_required('UPGRADE')
def add_permission():
    max_level = get_permission_num()
    next_permission_value = permission_value_by_level(max_level + 1)
    if next_permission_value > 98:
        result = {'status': 'Err', 'msg': u'添加失败,权限已达到上限'}
    else:
        created, ps = find_or_create_permission(value=next_permission_value, need_created=True)
        if created:
            db.session.commit()

        result = {'status': 'Ok', 'msg': u'添加成功'}

    return jsonify(result)


@bp.route('/add-role/', methods=['POST', ])
@login_required
@role_required('UPGRADE')
def add_role():
    new_role = request.form.get('newRole', "")
    new_label = request.form.get('newLabel', "")
    auto_add = request.form.get('autoSelect', True)

    if not new_label or not new_label:
        result = {'status': 'Err', 'msg': u'参数错误'}
    else:
        role_obj = get_role_by_name(role=new_role)
        if not role_obj:
            role_obj = create_role(role=new_role, label=new_label)

        result = {'status': 'Ok', 'msg': u'添加成功'}

        if auto_add == 'true':
            ps = get_permission_by_value(value=100)
            success, rst = add_role_to_permission(ps=ps, role=role_obj)
            result = {'status': 'Err', 'msg': rst} if not success else result
            ps = get_permission_by_value(value=99)
            success, rst = add_role_to_permission(ps=ps, role=role_obj)
            result = {'status': 'Err', 'msg': rst} if not success else result
            ps = get_permission_by_value(value=98)
            success, rst = add_role_to_permission(ps=ps, role=role_obj)
            result = {'status': 'Err', 'msg': rst} if not success else result

        if result['status'] == 'Ok':
            db.session.commit()
            # 更新game server端的permission表
            # tasks.update_permission_table([(ps.value, role_obj.role, role_obj.label)])

    return jsonify(result)


# Register blueprint
add_blueprint(bp)
