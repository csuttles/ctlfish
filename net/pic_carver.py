#!/usr/bin/env python3

import argparse
import cv2

from pathlib import Path
from scapy.all import *
from scapy.layers.http import HTTP


parser = argparse.ArgumentParser(sys.argv[0])
parser.add_argument('-f', '-faces', type=str, dest='faces', default='./faces',
                    help='path to store pictures with faces extracted from pcap')
parser.add_argument('-p', '--pictures', type=str, dest='pictures', default='./pictures',
                    help='patch to store pictures extracted from pcap')
parser.add_argument('-i' '--infile', type=str, dest='infile', default='pic_carver.pcap',
                    help='pcap file to read in')

parser.description = """\
This is a Python program to read a packet capture and pull images out of HTTP traffic, 
then detect faces in those images.
"""
args = parser.parse_args()


def face_detection(filepath, fname):
    # read image duh
    img = cv2.imread(filepath)
    # create cascade classifier from pre-trained model for frontal face recognition
    cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
    # rects - rectangles that contain faces in images stored as coordinates (x,y)
    # rects = cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCAL_IMAGE, (20, 20))
    rects = cascade.detectMultiScale(img, 1.3, 4, cv2.CASCADE_SCALE_IMAGE, (20, 20))

    if len(rects) == 0:
        # this means we didn't detect a face
        return False

    # if we got this far there are faces in the image, highlight them
    rects[:, 2:] += rects[:, :2]
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)
    # finally write the modified image and return True to indicate we found a face
    cv2.imwrite(f'{args.faces}/{args.infile}-{fname}', img)
    return True


def extract_image(pkt):
    image = None
    image_type = None

    try:
        if b'image' in pkt.Content_Type:
            # get image type and image data
            image_type = pkt.Content_Type.split(b'/')[1].split(b';')[0].decode('utf-8')
            image = pkt.load

            # this happens automagically because scapy http layer does it for us - yay! Thanks scapy!
            # decompress if compressed
            # try:
            #     if 'Content-Encoding' in headers:
            #         if headers['Content-Encoding'] == 'gzip':
            #             image = zlib.decompress(image, 16+zlib.MAX_WBITS)
            #         elif headers['Content-Encoding'] == 'deflate':
            #             image = zlib.decompress(image)
            # except:
            #     pass
    except:
        return None, None

    return image, image_type


def http_assembler(in_pcap):
    '''

    :param pcap: pcap file to carve images from
    :return: carved_images, faces detected (returned as counts)
    '''
    carved_images = 0
    faces_detected = 0

    pkts = sniff(offline=in_pcap, session=TCPSession)

    # filter to only packets with HTTPResponse
    ht = pkts.getlayer(scapy.layers.http.HTTPResponse)
    for pkt in ht:
        # print(type(pkt), pkt)
        image, image_type = extract_image(pkt)
        # print(f'image type: {image_type}')
        # print(f'image size: {len(image)}')
        if image is not None and image_type is not None:

            # store image: construct filename, open FD , write binary image to file, increment carved_images (id/count)
            # assemble path name and print msg
            file_name = f'{in_pcap}-pic_carver_{carved_images}.{image_type}'
            img_write_path = f'{args.pictures}/{file_name}'
            print(f'writing original image to: {img_write_path}')
            # ensure path exists and write image
            Path(args.pictures).mkdir(parents=True, exist_ok=True)
            with open(img_write_path, 'wb') as out_img:
                out_img.write(image)

            carved_images += 1

            # attempt face detection, and if successful, write image to faces dir
            try:
                result = face_detection(f'{args.pictures}/{file_name}', file_name)

                if result is True:
                    file_name = f'{in_pcap}-pic_carver_face_{carved_images}.{image_type}'
                    face_img_write_path = f'{args.faces}/{file_name}'
                    print(f'writing facial recognition edited image to: {face_img_write_path}')
                    Path(args.faces).mkdir(parents=True, exist_ok=True)
                    with open(face_img_write_path, 'wb') as out_img:
                        out_img.write(image)

                    faces_detected += 1
            except Exception as ex:
                print(f'caught exception: {ex.__class__.__name__} - {ex}')
                pass

    return carved_images, faces_detected


def main():
    carved_images, faces_detected = http_assembler(args.infile)
    print(f'all pictures in: {args.pictures}')
    print(f'pictures with faces in: {args.faces}')
    print(f'carved images: {carved_images}')
    print(f'faces detected: {faces_detected}')


if __name__ == '__main__':
    main()