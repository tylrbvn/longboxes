# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
import datetime

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

@auth.requires_login()
def new():
    #Form to create a new box
    form = FORM(DIV(LABEL('Name:', _for='name')),
                DIV(INPUT(_name='name', requires=IS_NOT_EMPTY())),
                DIV(LABEL('Public box:', _for='is_public'), INPUT(_name='is_public', _type='checkbox')),
                DIV(INPUT(_type='submit', _class = "btn btn-primary")))
    if form.accepts(request, session):
        query = ((db.box.owner_id == auth.user.id) & (db.box.name == form.vars.name))
        count = db(query).count()
        if (count == 0):
            db.box.insert(name=request.vars.name,
            is_public=request.vars.is_public,
            owner_id=auth.user.id,
            created_on = datetime.datetime.now())
            db.commit
            response.flash = "New box '" + form.vars.name + "' successfully created!"
        else:
            response.flash = "You already have a box called '" + form.vars.name + "', please enter a new name!"
    elif form.errors:
        response.flash = 'One or more of the entries is incorrect:'
    return dict(addform=form)

@auth.requires_login()
def add():
    #Retrieve box record using ID
    record = db.box(request.args(0))
    #Get list of users comics
    #TODO: Exclude comics that are already in box
    comics = db(db.comic.owner_id == auth.user.id).select()
    #Check if there exists a box with ID
    if (record):
        #Check user owns that box
        if (record.owner_id == auth.user.id):
            form = FORM(DIV("Select a comic: ",
                        SELECT(_name='comic',
                        *[OPTION(comics[i].title, _value=str(comics[i].id)) for i in range(len(comics))])),
                        DIV(INPUT(_type='submit', _value="Add", _class = "btn btn-primary"))
                        )
            if form.accepts(request, session):
                #Ensure comic not already in box
                count = db((db.comic_in_box.box_id == record.id) & (db.comic_in_box.comic_id == request.vars.comic)).count()
                if (count == 0):
                    db.comic_in_box.insert(comic_id = request.vars.comic,
                    box_id = record.id)
                    db.commit
                    response.flash = "Comic succesfully added to box '" + record.name + "'"
                else:
                    response.flash = "Error: '" + record.name + "' already contains this comic!"
            elif form.errors:
                response.flash = 'One or more of the entries is incorrect:'
            return dict(form = form, box_name = record.name)
    return dict()

@auth.requires_login()
def edit():
    #Retrieve comic record using ID
    record = db.box(request.args(0))
    db.box.id.readable = db.box.id.writable = False
    db.box.owner_id.readable = db.box.owner_id.writable = False
    db.box.created_on.readable = db.box.created_on.writable = False
    #Check if there exists a box with ID
    if(record):
        #Check user owns that box, disallow editing of Unfiled box
        if ((record.owner_id == auth.user.id) & (record.name != 'Unfiled')):
            edit=SQLFORM(db.box, record)
            if edit.accepts(request,session):
                response.flash = 'Box has been successfully updated.'
            elif edit.errors:
                response.flash = 'One or more of the entries is incorrect:'
            return dict(editform=edit)
    return dict()

@auth.requires_login()
def delete():
    #Delete box and add displaced comics to Unfiled
    #Don't allow the deletion of Unfiled or another users box
    return dict()

@auth.requires_login()
def view():
    box_id = request.args(0)
    if box_id is not None:
        boxes = db((db.box.id == box_id) & ((db.box.is_public == True) | (db.box.owner_id == auth.user.id)) & (db.box.owner_id == db.auth_user.id)).select()
        if len(boxes)>0:
            comics = db((db.comic_in_box.box_id == box_id) & (db.comic_in_box.comic_id == db.comic.id)).select()
            return dict(boxes = boxes, comics = comics)
    return dict()
