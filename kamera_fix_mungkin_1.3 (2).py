import numpy as np
import cv2 as cv
import serial
import time
import threading

# Inisialisasi objek serial
ser = serial.Serial('COM5', 115200, timeout=1.0)
print(ser)
time.sleep(3)
ser.reset_input_buffer()


# Menginisialisasi koordinat x sebagai None
global x_coord
x_coord = None


# Fungsi untuk mengirim koordinat x ke Arduino
def send_serial():
    global x_coord
    while True:
        time.sleep(0.1)  # Penundaan kecil untuk memberi waktu pada Arduino
        if x_coord is not None:
            # Mengirim koordinat x sebagai dua byte dengan byteorder 'big'
            print(x_coord)
            ser.write(x_coord.to_bytes(2, byteorder='big'))

# Fungsi untuk memproses gambar
def process_image():
    # Membuat objek VideoCapture untuk menangkap video dari kamera default (indeks kamera 2)
    global x_coord
    cap = cv.VideoCapture(2)

    while True:
        # Membaca frame dari kamera
        ret, img = cap.read()

        # Mengkonversi frame ke HSV
        img_to_thresh = cv.cvtColor(img, cv.COLOR_BGR2HSV)

        # Thresholding
        thresh = cv.inRange(img_to_thresh, (64, 59, 75), (93, 255, 255))

        # Deteksi kontur
        contours, hierarchy = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

        # Mengurutkan kontur berdasarkan area
        contours = sorted(contours, key=lambda x: cv.contourArea(x), reverse=True)

        # Menggambar kontur dan mengisi kontur terbesar
        result_flood = np.zeros_like(img)
        for contour in contours:
            convexHull = cv.convexHull(contour)
            cv.drawContours(thresh, [convexHull], -1, (255, 0, 0), 2)
            cv.fillPoly(result_flood, [convexHull], color=(255, 255, 255))

        # Mengisi area luar kontur yang terisi
        result_filly_po = result_flood.copy()
        mask = np.zeros((img.shape[0] + 2, img.shape[1] + 2), dtype=np.uint8)
        seed_point = (10, 10)
        cv.floodFill(result_flood, mask, seed_point, newVal=(255, 255, 255), loDiff=(20, 20, 20), upDiff=(20, 20, 20))
        result_flood_not = cv.bitwise_not(result_flood)

        # Menggabungkan hasil
        result_or = cv.bitwise_or(result_filly_po, result_flood_not)
        result_or_not = cv.bitwise_not(result_or)
        result_and = cv.bitwise_and(result_or, img_to_thresh)
        result_lapangan = cv.bitwise_or(result_or_not, result_and)

        # Proses tambahan dan deteksi kontur
        phresh = cv.inRange(result_lapangan, (0, 100, 100), (15, 255, 255))
        knl = np.ones((5, 5), np.uint8)
        mas = cv.morphologyEx(phresh, cv.MORPH_OPEN, knl)
        mas = cv.morphologyEx(mas, cv.MORPH_CLOSE, knl)
        cnts = cv.findContours(mas.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[-2]

        # Menggambar lingkaran pada gambar
        if len(cnts) > 0:
            c = max(cnts, key=cv.contourArea)
            ((x, y), radius) = cv.minEnclosingCircle(c)
            M = cv.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            if M["m00"] != 0:
                new_x_coord = int(M["m10"] / M["m00"])
                x_coord = new_x_coord


                if radius > 10:
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    cv.circle(img, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv.circle(img, center, 3, (0, 0, 255), -1)
                    cv.putText(img, "(" + str(center[0]) + "," + str(center[1]) + ")", (center[0] + 10, center[1] + 15),
                    cv.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        # Menampilkan frame
        cv.imshow("img", img)
        cv.imshow("thresh", thresh)
        cv.imshow("result lapangan", result_lapangan)
        cv.imshow("phresh", phresh)

        # Keluar jika tombol 'q' ditekan
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    # Melepaskan VideoCapture dan menutup semua jendela
    cap.release()
    cv.destroyAllWindows()
    
# Thread untuk mengirim koordinat x ke Arduino
serial_thread = threading.Thread(target=send_serial)
serial_thread.start()

# Thread untuk memproses gambar
image_thread = threading.Thread(target=process_image)
image_thread.start()

# Menunggu thread untuk selesai
serial_thread.join()
image_thread.join()


