# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

@auth.requires_login()
def new():
    db.comic.owner_id.readable = db.comic.owner_id.writable = False
    form = SQLFORM(db.comic)
    form.vars.owner_id = auth.user.id
    if form.accepts(request.vars, session):
        query = (db.box.owner_id == auth.user.id) & (db.box.name == 'Unfiled')
        unfiled_id = db.box(query).id
        db.comic_in_box.insert(comic_id = form.vars.id, box_id = unfiled_id)
        db.commit
        response.flash = "New comic '" + form.vars.title + "' has been added to your 'Unfiled' box."
    elif form.errors:
        response.flash = 'One or more of the entries is incorrect:'
    return dict(addform=form)

@auth.requires_login()
def add():
    #Retrieve box record using ID
    record = db.comic(request.args(0))
    #Get list of users comics
    #TODO: Exclude boxes that comic is already in
    boxes = db(db.box.owner_id == auth.user.id).select()
    #Check if there exists a comic with ID
    if (record):
        #Check user owns that comic
        if (record.owner_id == auth.user.id):
            form = FORM(DIV("Select a box: ",
                        SELECT(_name='box',
                        *[OPTION(boxes[i].name, _value=str(boxes[i].id)) for i in range(len(boxes))])),
                        DIV(INPUT(_type='submit', _value="Add", _class = "btn btn-primary"))
                        )
            if form.accepts(request, session):
                #Ensure comic not already in box
                count = db((db.comic_in_box.box_id == request.vars.box) & (db.comic_in_box.comic_id == record.id)).count()
                if (count == 0):
                    db.comic_in_box.insert(comic_id = record.id,
                    box_id = request.vars.box)
                    db.commit
                    response.flash = "'" + record.title + "' succesfully added to box"
                else:
                    response.flash = "Error: Selected box already contains '" + record.title + "'"
            elif form.errors:
                response.flash = 'One or more of the entries is incorrect:'
            return dict(form = form, comic_name = record.title)
    return dict()

@auth.requires_login()
def edit():
    #Retrieve comic record using ID
    record = db.comic(request.args(0))
    db.comic.id.readable = db.comic.id.writable = False
    db.comic.owner_id.readable = db.comic.owner_id.writable = False
    #Check if there exists a comic with ID
    if(record):
        #Check user owns that comic
        if (record.owner_id == auth.user.id):
            edit=SQLFORM(db.comic, record, deletable=True)
            if edit.accepts(request,session):
                response.flash = 'Comic has been successfully updated.'
            elif edit.errors:
                response.flash = 'One or more of the entries is incorrect:'
            return dict(editform=edit)
    return dict()


@auth.requires_login()
def view():
    comic_id = request.args(0)
    if comic_id is not None:
        #If own comic
        comics = db((db.comic.id == comic_id) & (db.comic.owner_id == auth.user.id) & (db.comic.owner_id == db.auth_user.id)).select()
        if len(comics)>0:
            return dict(comics = comics)
        else:
            #  If a comic from another user's public box
            public = db((db.comic_in_box.comic_id == comic_id) & (db.comic_in_box.box_id == db.box.id) & (db.box.is_public == True)).select()
            if len(public)>0:
                comics = db((db.comic.id == comic_id) & (db.comic.owner_id == db.auth_user.id)).select()
                return dict(comics = comics)
    return dict()
