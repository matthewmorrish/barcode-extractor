#!/usr/bin/env python3

"""

Barcode Extractor

Usage:
    python3 barcode_extractor.py [-h] -m {img,live} [-p [IMGPATH]]


Matthew Morrish

"""


# Imports
from pyzbar import pyzbar
import os, argparse, cv2, imutils


# Get image path
def get_ImgPath():
    for file in os.listdir(os.getcwd()):
        if file.split('.')[-1] in ['png', 'jpg', 'jpeg', 'gif']:
            return os.path.join(os.getcwd(), file)


# Get args
parser = argparse.ArgumentParser(description='Extract barcode data from loaded image or live feed.')
parser.add_argument(
    '-m', '--mode', help="Operation mode, 'img' for images or 'live' for live camera feed", 
    type=str, required=True, choices=('img', 'live'))
parser.add_argument(
    '-p', '--imgpath', help="Directory location for image if -m is 'img', default is first image detected in operating directory", 
    type=str, nargs='?', const=1, default=get_ImgPath())
args = parser.parse_args()


# Check for bad args
if args.mode == 'img' and args.imgpath == None:
    raise Exception('Please specify an image for barcode extraction')


# Extract barcodes from the image & return the data/data on image
def extractBarcodes(frame):

    # Specify which barcodes we want & set a place to store them
    barcode_li = []
    valid = ['CODABAR', 'CODE128', 'CODE39', 'CODE93', 'COMPOSITE', 
             'DATABAR', 'DATABAR_EXP', 'EAN13', 'EAN2', 'EAN5', 'EAN8',
             'I25', 'ISBN10', 'ISBN13','QRCODE', 'UPCA', 'UPCE']

    # Preprocess frame & extract
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, processed = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    barcodes = pyzbar.decode(processed, symbols=[getattr(pyzbar.ZBarSymbol, i) for i in valid])

    # Loop over the detected barcodes
    for barcode in barcodes:

        # Draw the bounding box location
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)

        # Convert barcode data from bytes object to str, add it to barcode_li
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        barcode_li.append({'type': barcodeType, 'data': barcodeData})

        # Draw the barcode data and type on the image
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.4, (0, 0, 255), 1)

    return barcode_li, frame


# Main 
def main():

    # Set vars
    title = os.path.abspath(__file__).split("\\")[-1]

    # On -m = live
    if args.mode == 'live':

        # Set live vars & make things legible
        detected = []
        print(f'\n[{title}] running on live capture...')

        # Begin capture and set resolution
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, 1920)
        cap.set(4, 1080)

        # Iteratively detect and extract barcodes on each frame
        while 1:
            _, frame = cap.read()
            extracted_data, extracted_img = extractBarcodes(frame)
            cv2.imshow(title, extracted_img)

            # Update user on extracted information
            for i in extracted_data:
                if i not in detected:
                    detected.append(i)
                    print(f"[INFO] Found {i['type']} barcode: {i['data']}")

            if cv2.waitKey(1) & 0xFF == 27:
                break

        # Release the capture
        cap.release()

    # On -m = img
    else:

        # Make things legible
        print(f'\n[{title}] running on loaded image...')

        # Load the image, extract barcodes
        frame = cv2.imread(args.imgpath)
        extracted_data, extracted_img = extractBarcodes(frame)

        # Update user on extracted information
        for i in extracted_data:
            print(f"[INFO] Found {i['type']} barcode: {i['data']}")

        # Display data on image
        cv2.imshow(title, extracted_img)
        cv2.waitKey()

    # Clean up when done
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()