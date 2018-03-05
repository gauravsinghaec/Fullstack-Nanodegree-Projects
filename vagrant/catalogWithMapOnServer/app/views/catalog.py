from .globalfile import session, login_required, ownership_required, \
                        createItem, removeItem, updateItem,\
                        getUserById, checkDuplicateItem
from app import login_session, func, flash, \
                        url_for, redirect, request, \
                        Blueprint, render_template, \
                        Item


catalog = Blueprint('catalog', __name__)

@catalog.route('/')
# @catalog.route('/catalog')
def landingPage():
    items = session.query(Item).order_by('last_updated desc').all()
    categories = session.query(Item.category, func.count(
        Item.category)).group_by(Item.category).all()

    # Below code show how to use HTML Template to achieve the same dynamically
    if('username' in login_session 
        # and checkAccessToken()
        ):
        return render_template('main.html',
                               session=login_session,
                               items=items,
                               categories=categories,
                               pagetitle='Home')
    else:
        return render_template('publicmain.html',
                               session=login_session,
                               items=items,
                               categories=categories,
                               pagetitle='Home')


@catalog.route('/<category>')
@catalog.route('/<category>/items')
def getCatalogItems(category):
    categories = session.query(Item.category, func.count(
        Item.category)).group_by(Item.category).all()
    items = session.query(Item).filter_by(
        category=category).order_by('last_updated desc').all()
    if items != []:
        return render_template('catalog/items.html', session=login_session,
                               items=items, categories=categories,
                               pagetitle='Items')
    else:
        return redirect(url_for('catalog.landingPage'))


@catalog.route('/<category>/<itemname>')
def getCatalogItemDetails(category, itemname):
    item = session.query(Item).filter_by(
        category=category, title=itemname).one()
    itemCreator = getUserById(item.user_id)
    if ('username' not in login_session or
            itemCreator.id != login_session['user_id']):
        return render_template('catalog/publicitemdetail.html', session=login_session,
                               item=item, category=category,
                               pagetitle='Items')
    return render_template('catalog/itemdetail.html', session=login_session,
                           item=item, category=category,
                           pagetitle='Items')


@catalog.route('/new', methods=['GET', 'POST'])
@login_required
def newItem():
    if request.method == 'POST':
    	if checkDuplicateItem(request.form['title'],request.form['category']):
    		flash('Item already exists under the selected category')	
        	return render_template('catalog/newitem.html',
        	                   session=login_session, pagetitle='New Items')
        createItem(request.form['title'], request.form['description'],
                   request.form['category'], login_session['user_id'])
        flash('New item created')
        return redirect(url_for('catalog.getCatalogItems',
                                category=request.form['category']))
    else:
        return render_template('catalog/newitem.html',
                               session=login_session, pagetitle='New Items')


@catalog.route('/<int:item_id>/<itemname>/edit', methods=['GET', 'POST'])
@login_required
@ownership_required
def editItem(item_id, itemname):
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    if request.method == 'POST':
        if item != []:
            fields = {}
            fields['title'] = request.form['title']
            fields['description'] = request.form['description']
            fields['category'] = request.form['category']
            if checkDuplicateItem(fields['title'],fields['category']):
            	flash('Item already exists under the selected category')	
            	return render_template('catalog/edititem.html',session=login_session,
            	                   item=item, pagetitle='Edit Items')            
            updateItem(item=item, **fields)
            flash('Item "' + item.title + '" updated successfully')
        return redirect(url_for('catalog.getCatalogItems',
                                category=fields['category']))
    else:
        return render_template('catalog/edititem.html', session=login_session,
                               item=item, pagetitle='Edit Items')


@catalog.route('/<int:item_id>/<itemname>/delete', methods=['GET', 'POST'])
@login_required
@ownership_required
def deleteItem(item_id, itemname):
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    if request.method == 'POST':
        if item != []:
            removeItem(item=item)
            flash('Item "' + item.title + '" deleted successfully')
        return redirect(url_for('catalog.getCatalogItems', category=item.category))
    else:
        return render_template('catalog/deleteitem.html', session=login_session,
                               item=item, pagetitle='Delete Items')


