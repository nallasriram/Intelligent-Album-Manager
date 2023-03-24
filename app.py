import os
import threading
from typing import Text
from flask import Flask, request, render_template
from gevent.pywsgi import WSGIServer
import boto3
access_key_id = 'AKIAQ5O73G7DSIQ5HC66'			
secret_access_key = '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'	
client=boto3.client('rekognition',aws_access_key_id = access_key_id ,aws_secret_access_key = secret_access_key,region_name = 'ap-south-1')
s3 = boto3.client('s3',aws_access_key_id = access_key_id ,aws_secret_access_key = secret_access_key,region_name = 'ap-south-1')
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('base.html')

@app.route('/index.html',methods = ['GET','POST'])
def upload():
    if request.method == 'POST':
        f = request.files['image']
        print('Image name : ',f)
        print("current path")
        base_path = os.path.dirname(__file__)
        print("current_path",base_path)
        filepath = os.path.join(base_path,'uploads',f.filename)
        print("upload folder is ",filepath)
        f.save(filepath)

        text = main(filepath)
    return text
# @app.route('/pred',methods=['GET','POST'])
# def pred():
#     if request.method=='POST':
#         some = request.files['image']
    # return render_template('base.html',d=some)
def main(filepath):
    bucket= 'vitbucketalbum'										
    collection_id = 'Intelligent_Album_Faces'
    filename = filepath
    relative_filename = os.path.split(filepath)[1]
    fileNames=[relative_filename]
    s3.upload_file(filename,bucket,relative_filename)
    print("file Uploaded")

    threshold = 70										
    maxFaces = 2
    for fileName in fileNames:
        response=client.search_faces_by_image(CollectionId=collection_id,
                                Image={'S3Object':{'Bucket':bucket,'Name':fileName}},
                                FaceMatchThreshold=threshold,
                                MaxFaces=maxFaces)
        faceMatches=response['FaceMatches']
        print ('Matching faces')
        for match in faceMatches:
            print ('FaceId: ' + match['Face']['FaceId'])
            print ('External Id: ' +match['Face']['ExternalImageId'])
            print ('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
            copy_from = str(bucket+'/'+fileName)																			
            move_to = str(match['Face']["ExternalImageId"][:-4]+'/' +fileName)
            recognized_person_name = str(match['Face']['ExternalImageId'][:-4])								
            s3.copy_object(Bucket=bucket, CopySource=copy_from, Key=move_to)																				
            print("successfully moved to " +move_to)
            f = str(match['Face']['ExternalImageId']) 
        
        return render_template('index.html',data=f,d=recognized_person_name)
        # return move_to
if __name__ == "__main__":
    app.run(debug=True, threaded = False)