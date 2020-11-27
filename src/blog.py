from flask import (Blueprint, flash, g, redirect, render_template, request, url_for, session)
from werkzeug.exceptions import abort
from src.auth import login_required
from src.merakiApi import *
from src.db import get_db
import datetime
import pytz
import os
import PIL

bp = Blueprint('blog', __name__)


@bp.route('/')
@login_required
def index():
    """
    Index page - No Content
    :return:
    """
    return render_template('index.html')


@bp.route('/home', methods=('GET', 'POST'))
@login_required
def home():
    """
    Application Home page
    :return:
    """
    error = None
    # Retrieve current Organization
    organization = {'id': '', 'name': ''}
    if 'orgID' not in session:
        error = 'WARNING: No Organization selected! Please configure in Settings tab'
    else:
        organization['id'] = session['orgID']
        organization['name'] = session['orgNAME']

    # If no Organization is selected
    if error is not None:
        flash(error)
        return render_template('blog/home.html', org=organization, networks=[])

    else:
        # Display most recent Multisite Snapshot
        recentSnap = None
        recentSnap_List = []
        if 'snapShot' in session:
            db = get_db()
            recentSnap = session['snapShot']
            for snap in recentSnap:
                snap_DB = db.execute(
                    'SELECT * FROM snaps WHERE url = ?', (snap['url'],)
                ).fetchone()
                if snap_DB is not None:
                    snapInfo = []
                    for info in snap_DB:
                        snapInfo.append(info)
                    recentSnap_List.append(snapInfo)

        # Get current Organization networks
        networks = getNetworks(session['orgID'])

        # When user selects Networks and Clicks the Submit button
        if request.method == 'POST':
            # Get Network Selections
            network_Selections = request.form.getlist('network')
            network_Selections_Detailed = []
            for network in network_Selections:
                # Identify the selected networks and save related info
                for n in networks:
                    if network == n['id']:
                        network_Detail = {
                            'id': n['id'],
                            'name': n['name'],
                            'timeZone': n['timeZone']
                        }
                        print('{} selected! (Current local time: {})'.format(network_Detail['name'], network_Detail['timeZone']))
                        network_Selections_Detailed.append(network_Detail)
            # Store selected Network Info in Session
            session['selectedNetworks'] = network_Selections_Detailed

            return redirect(url_for('blog.takeSnap'))
        # Display Home Page
        return render_template('blog/home.html', org=organization, networks=networks, recentSnap=recentSnap_List)


@bp.route('/takeSnap', methods=('GET', 'POST'))
@login_required
def takeSnap():
    """
    Application Take Snapshot page
    :return:
    """
    error = None
    # Retrieve current Organization
    organization = {
        'id': session['orgID'],
        'name': session['orgNAME']
    }

    # Retrieve selected Networks
    selectedNetworks = session['selectedNetworks']
    complete_Network_Camera_List = []

    for network in selectedNetworks:
        network_Info = {
            'id': network['id'],
            'name': network['name'],
            'timeZone': network['timeZone']
        }

        # Get Network devices
        network_Camera_List = []
        network_Devices = getNetworkDevices(network['id'])

        for device in network_Devices:
            # Filter MV camera
            if 'MV' in device['model']:
                mvCamera = {}

                if 'name' not in device:
                    mvCamera['name'] = 'Unnamed Device'
                else:
                    mvCamera['name'] = device['name']

                if 'serial' not in device:
                    error = 'ERROR: Camera Serial Number missing! Network:{} -- Device {}'.format(
                        network['name'], device['serial'])
                    flash(error)
                    return render_template('blog/takeSnap.html', org=organization, networks=selectedNetworks)
                else:
                    mvCamera['serial'] = device['serial']

                network_Camera_List.append(mvCamera)
                # selectedCameras.append(mvCamera)

        network_Info['cameraList'] = network_Camera_List
        complete_Network_Camera_List.append(network_Info)

    # Store selected Networks and their MV Cameras in Session
    session['completeNetworkCameraList'] = complete_Network_Camera_List

    # When user selects Network Cameras and clicks the Snap button
    if request.method == 'POST':
        # Clear Session for new snap
        session.pop('snapShot', None)
        snapShot = []

        useCustomTime = request.form.get('selectTime')
        camera_Selections = request.form.getlist('camera')

        # For each of the selected Networks, Check if it contains one of the selected cameras
        for network in complete_Network_Camera_List:
            network_Name = network['name']
            network_TimeZone = pytz.timezone(network['timeZone'])

            timeStamp = datetime.datetime.now(tz=network_TimeZone)
            timeStamp = timeStamp - datetime.timedelta(minutes=5, seconds=0)
            timeStamp = timeStamp.isoformat(timespec='seconds')

            for camera in network['cameraList']:
                if camera['serial'] in camera_Selections:
                    selected_Camera_Name = camera['name']

                    # Check if user input custom time
                    if useCustomTime == 'on':
                        inputDate = request.form.get('customDate')
                        inputTime = request.form.get('customTime')
                        customDate_and_Time = inputDate + " " + inputTime
                        timeStamp = datetime.datetime.strptime(customDate_and_Time, '%Y-%m-%d %H:%M')
                        timeStamp = timeStamp - datetime.timedelta(minutes=5, seconds=0)
                        timeStamp = timeStamp.isoformat(timespec='seconds')

                    # Take snapshot
                    print('SNAPPING: {} (from {}) @ {}'.format(selected_Camera_Name, network_Name, timeStamp))
                    snap = getCameraScreenshot(camera['serial'], timeStamp)
                    snap['network'] = network_Name
                    snap['timestamp'] = timeStamp
                    snap['camera'] = selected_Camera_Name

                    # On Success
                    if 'errors' not in snap:
                        snapShot.append(snap)

                    # On failure
                    else:
                        details = ': {}(@{})'.format(snap['camera'], timeStamp)
                        error = snap['errors'][0] + details
                        flash(error)

        # Store ALL Snap Shots in Session
        session['snapShot'] = snapShot
        return redirect(url_for('blog.snapshot'))

    # Display Take a Snap page
    return render_template('blog/takeSnap.html', org=organization, networks_with_Devices=complete_Network_Camera_List)


@bp.route('/snapshot', methods=('GET', 'POST'))
@login_required
def snapshot():
    """
    Application Home page
    :return:
    """
    error = None
    # Get current Snap Shot
    snapShot = session['snapShot']
    for pic in snapShot:
        # Commit Snap to DB
        commitSnap(pic)

    # Clean up session variables and return to home
    session.pop('selectedNetworks', None)
    session.pop('selectedCameras', None)
    return redirect(url_for('blog.home'))


def commitSnap(picture):
    """
    Commit MV camera Snapshot and Info to DB
    :param picture: Dictionary of information about a Snap
    :return:
    """
    db = get_db()
    # cwd = os.getcwd()
    # fullPath = cwd + localPath
    picture['camera'] = picture['camera'].replace(' ', '_')
    localImage = '{}_{}.jpeg'.format(picture['camera'], picture['timestamp'])
    path = '../GVE_DevNet_Meraki_MultiSite_Snapshot/src/static/img/SnapShots/{}'.format(localImage)
    localPath = url_for('static', filename='img/SnapShots/{}'.format(localImage))

    try:
        # Create local copy of image
        response = requests.get(picture['url'])
        image = Image.open(BytesIO(response.content))
        image.save(path)
    except PIL.UnidentifiedImageError:
        commitSnap(picture)

    try:
        db.execute(
            'INSERT OR IGNORE INTO snaps (id, url, expire, network, timestamp, camera, localURL) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (session['user_id'], picture['url'], picture['expiry'], picture['network'], picture['timestamp'],
             picture['camera'], localPath)
        )
        db.commit()
        return
    except AttributeError:
        commitSnap(picture)


@bp.route('/snaps', methods=('GET', 'POST'))
@login_required
def snaps():
    """
    Application Previous Snaps page
    :return:
    """
    error = None
    db = get_db()

    snapShots_From_DB = db.execute(
        'SELECT * FROM snaps WHERE id = ?', (session['user_id'],)
    ).fetchall()

    user_Snapshots = []
    for db_Snaps in snapShots_From_DB:
        snapInfo = []
        for info in db_Snaps:
            snapInfo.append(info)
        user_Snapshots.append(snapInfo)

    return render_template('blog/snaps.html', user_Snapshots=user_Snapshots)


@bp.route('/schedule', methods=('GET', 'POST'))
@login_required
def scheduledSnap():
    """
    Application Take Snapshot page
    :return:
    """
    error = None
    if 'schedule' not in session:
        session['schedule'] = []

    if request.method == 'POST':
        currentScheduleList = session['schedule']
        session.pop('schedule', None)
        scheduled_Days = request.form.getlist('day')
        scheduled_Time = request.form.get('scheduledTime')
        scheduled_Repeat = request.form.get('scheduledNumber')
        new_Schedule = 'Scheduled Snapshots on {} @ {} for the next {} weeks!'.format(scheduled_Days, scheduled_Time, scheduled_Repeat)
        currentScheduleList.append(new_Schedule)
        session['schedule'] = currentScheduleList
        return render_template('blog/scheduledSnap.html', schedule=session['schedule'])
    return render_template('blog/scheduledSnap.html', schedule=session['schedule'])


@bp.route('/settings', methods=('GET', 'POST'))
@login_required
def settings():
    """
    Application Settings page
    :return:
    """
    username = g.user['username']
    password = g.user['password']
    accessToken = g.user['accessToken']

    orgs = getOrgs()

    if request.method == 'POST':
        clearSchedule = request.form.get('clearSchedule')
        if clearSchedule == 'on':
            session.pop('schedule', None)

        session.pop('orgID', None)
        session.pop('orgNAME', None)
        orgId = request.form['orgId']
        orgDetails = getOrg(orgId)
        session['orgID'] = orgDetails['id']
        session['orgNAME'] = orgDetails['name']
        return redirect(url_for('blog.home'))

    return render_template('blog/settings.html', username=username, password=password,
                           accessToken=accessToken, orgs=orgs)
