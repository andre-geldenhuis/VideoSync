import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
import model
import convert_to_webm as convert
import datetime


UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['mp4'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    video1 = model.session.query(model.Track).get(1)
    video2 = model.session.query(model.Track).get(2)
    return render_template("index.html", video1=video1, video2=video2)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file1 = request.files['file1']
        file2 = request.files['file2']

        if (file1 and allowed_file(file1.filename)) and (file2 and allowed_file(file2.filename)):
            filename1 = secure_filename(file1.filename)
            filename2 = secure_filename(file2.filename)

            # upload file
            file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))

            # save files info in db
            # save file 1
            new_filename1 = filename1
            new_title = request.form.get("title")
            new_artist = request.form.get("artist")
            new_event = request.form.get("event")
            new_path = UPLOAD_FOLDER
            new_filename_webm1 = convert.convert_video(filename1, UPLOAD_FOLDER)  # convert file to webm
            new_file1 = model.Track(title=new_title, filename=new_filename1,
                                    artist=new_artist, event=new_event, path=new_path,
                                    filename_webm=new_filename_webm1)
            model.session.add(new_file1)

            # save file 2
            new_filename2 = filename2
            new_filename_webm2 = convert.convert_video(filename2, UPLOAD_FOLDER)  # convert file to webm
            new_file2 = model.Track(title=new_title, filename=new_filename2,
                                    artist=new_artist, event=new_event, path=new_path,
                                    filename_webm=new_filename_webm2)
            model.session.add(new_file2)


            # analyze files

            # save group info into db
            new_timestamp = datetime.datetime.now()
            new_group = model.Group(timestamp=new_timestamp)
            model.session.add(new_group)

            # save analysis into db
            new_group_id = 100  # how to automate this part
            new_track_id1 = 100  # get this from above info?
            new_sync_point1 = 100
            new_analysis1 = model.Analysis(group_id=new_group_id, track_id=new_track_id1,
                                           sync_point=new_sync_point1)
            model.session.add(new_analysis1)

            new_track_id2 = 200  # how to automate this part
            new_sync_point2 = 200  # get this from above info?
            new_analysis2 = model.Analysis(group_id=new_group_id, track_id=new_track_id2,
                                           sync_point=new_sync_point2)
            model.session.add(new_analysis2)


            model.session.commit()


            return redirect('/view')

    return render_template('upload.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/view')
def view():
    groups = model.session.query(model.Group).all()

    return render_template("view.html", groups=groups)


@app.route('/view_event')
def view_event():
    group_id = request.args.get("group_id")
    video_group = model.session.query(model.Group).get(group_id)
    groups = model.session.query(model.Group).all()

    return render_template("view_event.html", video_group=video_group, groups=groups)


if __name__ == "__main__":
    app.run(debug=True)
