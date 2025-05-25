import cv2
import numpy as np
import os
from fpdf import FPDF
from tkinter import Tk, filedialog, Button, Label, Frame, Canvas, BOTH, TOP, BOTTOM, LEFT, RIGHT
from PIL import Image, ImageTk

class DocumentScanner:
    def __init__(self):
        self.image = None
        self.orig_image = None
        self.processed_image = None
        self.warped_image = None
        self.corners = None
        self.pdf_path = None
        self.width = 0
        self.height = 0
        self.setup_gui()
        
    def setup_gui(self):
        """Grafik kullanıcı arayüzünü ayarlar"""
        self.root = Tk()
        self.root.title("Belge Tarama Uygulaması")
        self.root.geometry("1000x600")
        
        # Ana çerçeveyi oluştur
        main_frame = Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Üst çerçeve - düğmeler için
        top_frame = Frame(main_frame)
        top_frame.pack(side=TOP, fill='x', pady=10)
        
        # Görüntü çerçevesi
        self.image_frame = Frame(main_frame, bg='lightgray')
        self.image_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Resim yükleme düğmesi
        load_btn = Button(top_frame, text="Fotoğraf Yükle", command=self.load_image)
        load_btn.pack(side=LEFT, padx=5)
        
        # İşleme düğmesi
        self.process_btn = Button(top_frame, text="Belgeyi İşle", command=self.process_document, state='disabled')
        self.process_btn.pack(side=LEFT, padx=5)
        
        # PDF olarak kaydetme düğmesi
        self.save_pdf_btn = Button(top_frame, text="PDF Olarak Kaydet", command=self.save_as_pdf, state='disabled')
        self.save_pdf_btn.pack(side=LEFT, padx=5)
        
        # Görüntü için canvas oluştur
        self.canvas = Canvas(self.image_frame, bg='lightgray')
        self.canvas.pack(fill=BOTH, expand=True)
        
        # Canvas tıklama olaylarını dinle (köşeleri manuel düzeltmek için)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        
        # Durum bildirimi
        self.status_label = Label(main_frame, text="Hoş geldiniz! Lütfen bir fotoğraf yükleyin.", bd=1, relief='sunken', anchor='w')
        self.status_label.pack(side=BOTTOM, fill='x')
    
    def load_image(self):
        """Kullanıcının dosya seçmesini sağlar ve görüntüyü yükler"""
        file_path = filedialog.askopenfilename(
            title="Fotoğraf Seç",
            filetypes=[("Görüntü Dosyaları", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if not file_path:
            return
            
        # OpenCV ile görüntüyü oku
        self.orig_image = cv2.imread(file_path)
        if self.orig_image is None:
            self.status_label.config(text="Görüntü yüklenemedi!")
            return
            
        # Görüntüyü BGR'dan RGB'ye dönüştür (gösterim için)
        self.image = cv2.cvtColor(self.orig_image, cv2.COLOR_BGR2RGB)
        
        # Görüntü boyutlarını sakla
        self.height, self.width = self.image.shape[:2]
        
        # Canvas boyutuna göre görüntüyü yeniden boyutlandır
        self.display_image(self.image)
        
        # Otomatik köşe tespiti yap
        self.detect_document_corners()
        
        # Düğme durumlarını güncelle
        self.process_btn.config(state='normal')
        self.status_label.config(text=f"Görüntü yüklendi: {os.path.basename(file_path)}")
    
    def display_image(self, image, corners=None):
        """Görüntüyü canvas'a yerleştirir ve gerekirse köşeleri çizer"""
        # Canvas boyutlarını al
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas henüz hazır değil, kısa bir bekleme sonrası tekrar dene
            self.root.after(100, lambda: self.display_image(image, corners))
            return
        
        # Görüntüyü canvas boyutuna göre ölçeklendir
        scale = min(canvas_width / self.width, canvas_height / self.height) * 0.9
        new_width = int(self.width * scale)
        new_height = int(self.height * scale)
        
        # PIL ile yeniden boyutlandır
        pil_img = Image.fromarray(image)
        resized_img = pil_img.resize((new_width, new_height), Image.LANCZOS)
        
        # Tkinter için PhotoImage'e dönüştür
        self.tk_image = ImageTk.PhotoImage(resized_img)
        
        # Canvas'ı temizle ve yeni görüntüyü yerleştir
        self.canvas.delete("all")
        img_x = (canvas_width - new_width) // 2
        img_y = (canvas_height - new_height) // 2
        self.canvas.create_image(img_x, img_y, anchor='nw', image=self.tk_image)
        
        # Ölçek faktörünü kaydet (orijinal görüntü koordinatlarına dönüşüm için)
        self.scale_factor = scale
        self.img_x = img_x
        self.img_y = img_y
        
        # Köşeleri çiz (varsa)
        if corners is not None:
            for i, (x, y) in enumerate(corners):
                # Görüntü koordinatlarını canvas koordinatlarına dönüştür
                canvas_x = int(x * scale) + img_x
                canvas_y = int(y * scale) + img_y
                
                # Köşeleri çiz (10x10 kare)
                color = "red" if i == 0 else "blue" if i == 1 else "green" if i == 2 else "purple"
                self.canvas.create_rectangle(canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5, 
                                            fill=color, outline=color, tags=f"corner{i}")
                
            # Köşeleri birleştiren çizgileri çiz
            for i in range(4):
                start_x = int(corners[i][0] * scale) + img_x
                start_y = int(corners[i][1] * scale) + img_y
                end_x = int(corners[(i+1)%4][0] * scale) + img_x
                end_y = int(corners[(i+1)%4][1] * scale) + img_y
                self.canvas.create_line(start_x, start_y, end_x, end_y, fill="cyan", width=2)
    
    def detect_document_corners(self):
        """Görüntüdeki belgenin köşelerini otomatik olarak tespit eder"""
        # Görüntüyü gri tonlamaya dönüştür
        gray = cv2.cvtColor(self.orig_image, cv2.COLOR_BGR2GRAY)
        
        # Gauss bulanıklaştırması uygula
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Kenar tespiti (Canny)
        edges = cv2.Canny(blurred, 75, 200)
        
        # Konturları bul
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # Konturları alanlarına göre sırala (büyükten küçüğe)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        
        # Dört köşeli en iyi konturu bul
        target_contour = None
        
        for contour in contours:
            # Konturu yaklaşık olarak poligonla temsil et
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            
            # Dört köşeli bir konturu bulduk mu?
            if len(approx) == 4:
                target_contour = approx
                break
        
        # Eğer uygun bir kontur bulunmazsa, görüntünün köşelerini kullan
        if target_contour is None:
            self.corners = np.array([
                [0, 0],                   # sol üst
                [self.width - 1, 0],      # sağ üst
                [self.width - 1, self.height - 1], # sağ alt
                [0, self.height - 1]      # sol alt
            ])
        else:
            # Kontur köşelerini sıralama (sol üst, sağ üst, sağ alt, sol alt sırasıyla)
            self.corners = self.order_points(target_contour.reshape(4, 2))
        
        # Köşeleri çiz
        self.display_image(self.image, self.corners)
        self.status_label.config(text="Belge köşeleri tespit edildi. Gerekirse köşeleri manuel olarak ayarlayabilirsiniz.")
        
    def order_points(self, pts):
        """Köşe noktalarını sol üst, sağ üst, sağ alt, sol alt sırasına göre sıralar"""
        rect = np.zeros((4, 2), dtype=np.float32)
        
        # Toplam koordinatları bul
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # sol üst
        rect[2] = pts[np.argmax(s)]  # sağ alt
        
        # y-x farkını bul
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # sağ üst
        rect[3] = pts[np.argmax(diff)]  # sol alt
        
        return rect
    
    def on_canvas_click(self, event):
        """Canvas üzerinde tıklama olayını işler - köşe noktalarını seçer"""
        if self.corners is None:
            return
            
        # En yakın köşeyi bul
        closest_corner = -1
        min_distance = float('inf')
        
        for i in range(4):
            corner_x = int(self.corners[i][0] * self.scale_factor) + self.img_x
            corner_y = int(self.corners[i][1] * self.scale_factor) + self.img_y
            
            dist = (corner_x - event.x)**2 + (corner_y - event.y)**2
            if dist < min_distance:
                min_distance = dist
                closest_corner = i
                
        # Yakınlık kontrolü (15 piksel içindeyse)
        if min_distance <= 225:  # 15^2
            self.active_corner = closest_corner
        else:
            self.active_corner = None
    
    def on_canvas_drag(self, event):
        """Canvas üzerinde sürükleme olayını işler - köşe noktalarını günceller"""
        if self.active_corner is not None and self.corners is not None:
            # Canvas koordinatlarını görüntü koordinatlarına dönüştür
            img_x = (event.x - self.img_x) / self.scale_factor
            img_y = (event.y - self.img_y) / self.scale_factor
            
            # Görüntü sınırları içinde olduğundan emin ol
            img_x = max(0, min(img_x, self.width - 1))
            img_y = max(0, min(img_y, self.height - 1))
            
            # Köşeyi güncelle
            self.corners[self.active_corner] = [img_x, img_y]
            
            # Görüntüyü yeniden çiz
            self.display_image(self.image, self.corners)
    
    
    def enhance_document(self, image):
        """İşlenmiş belgeyi iyileştirir - kontrast artırma, gürültü azaltma vb."""
        # Gri tonlama dönüşümü
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Kontrast artırma
        xp = [0, 64, 128, 192, 255]
        fp = [0, 16, 128, 240, 255]

        x = np.arange(256)

        table = np.interp(x, xp, fp).astype('uint8')
        enhanced = cv2.LUT(gray, table)
        
        # Gürültü azaltma
        enhanced = cv2.blur(enhanced, (5, 5))

        # Keskinleştirme
        kernel = np.array([
            [0, -1, 0],
            [-1, 7, -1],
            [0, -1, 0]
        ], dtype = np.float32)
    
        kernel = kernel / 3
    
        sharpened = cv2.filter2D(enhanced, -1, kernel)
    
        return sharpened
        

    def process_document(self):
        """Tespit edilen köşelere göre perspektif dönüşümü uygular"""
        if self.corners is None:
            self.status_label.config(text="Lütfen önce bir görüntü yükleyin!")
            return
            
        # Perspektif dönüşümü için hedef boyutları hesapla
        # (A4 oranına yakın bir sonuç için)
        width_a = np.sqrt(((self.corners[2][0] - self.corners[3][0]) ** 2) + 
                          ((self.corners[2][1] - self.corners[3][1]) ** 2))
        width_b = np.sqrt(((self.corners[1][0] - self.corners[0][0]) ** 2) + 
                          ((self.corners[1][1] - self.corners[0][1]) ** 2))
        max_width = max(int(width_a), int(width_b))
        
        height_a = np.sqrt(((self.corners[1][0] - self.corners[2][0]) ** 2) + 
                           ((self.corners[1][1] - self.corners[2][1]) ** 2))
        height_b = np.sqrt(((self.corners[0][0] - self.corners[3][0]) ** 2) + 
                           ((self.corners[0][1] - self.corners[3][1]) ** 2))
        max_height = max(int(height_a), int(height_b))
        
        # A4 oranına uyarla (yaklaşık 1:1.414)
        if max_width / max_height > 1:  # yatay belge
            max_height = int(max_width / 1.414)
        else:  # dikey belge
            max_width = int(max_height / 1.414)
        
        # Hedef köşe noktaları
        dst_points = np.array([
            [0, 0],               # sol üst
            [max_width - 1, 0],   # sağ üst
            [max_width - 1, max_height - 1], # sağ alt
            [0, max_height - 1]   # sol alt
        ], dtype=np.float32)
        
        # Perspektif dönüşüm matrisini hesapla
        M = cv2.getPerspectiveTransform(self.corners.astype(np.float32), dst_points)
        
        # Dönüşümü uygula
        self.warped_image = cv2.warpPerspective(self.orig_image, M, (max_width, max_height))
        
        # Görüntü iyileştirme işlemleri
        self.processed_image = self.enhance_document(self.warped_image)
        
        # İşlenmiş görüntüyü göster
        processed_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
        self.display_image(processed_rgb)
        
        # PDF kaydetme düğmesini etkinleştir
        self.save_pdf_btn.config(state='normal')
        self.status_label.config(text="Belge başarıyla işlendi! PDF olarak kaydedebilirsiniz.")


    def save_as_pdf(self):
        """İşlenmiş belgeyi PDF olarak kaydeder"""
        if self.processed_image is None:
            self.status_label.config(text="Lütfen önce belgeyi işleyin!")
            return
            
        # Kaydetme dosya yolu seç
        file_path = filedialog.asksaveasfilename(
            title="PDF Olarak Kaydet",
            defaultextension=".pdf",
            filetypes=[("PDF Dosyaları", "*.pdf")]
        )
        
        if not file_path:
            return
            
        try:
            # İşlenmiş görüntüyü geçici bir dosya olarak kaydet
            temp_img_path = "temp_scan.jpg"
            cv2.imwrite(temp_img_path, self.processed_image)
            
            # PDF oluştur
            pdf = FPDF()
            
            # A4 boyutu: 210 x 297 mm
            pdf.add_page()
            
            # Görüntüyü sayfaya ekle (sayfa boyutuna sığdır)
            img_height, img_width = self.processed_image.shape[:2]
            aspect = img_width / img_height
            
            # A4 kağıdında güvenli alan (kenar boşlukları için)
            page_width = 190  # mm
            page_height = 277  # mm
            
            # En-boy oranına göre boyutlandırma
            if aspect > page_width / page_height:  # görüntü daha geniş
                width = page_width
                height = page_width / aspect
            else:  # görüntü daha uzun
                height = page_height
                width = page_height * aspect
            
            # Sayfayı ortalamak için kenar boşluğu
            x_margin = (210 - width) / 2
            y_margin = (297 - height) / 2
            
            pdf.image(temp_img_path, x=x_margin, y=y_margin, w=width, h=height)
            
            # PDF'i kaydet
            pdf.output(file_path)
            
            # Geçici dosyayı temizle
            os.remove(temp_img_path)
            
            self.pdf_path = file_path
            self.status_label.config(text=f"PDF başarıyla kaydedildi: {os.path.basename(file_path)}")
            
        except Exception as e:
            self.status_label.config(text=f"PDF kaydedilirken hata oluştu: {str(e)}")
    
    def run(self):
        """Uygulamayı başlatır"""
        self.root.mainloop()

# Ana program
if __name__ == "__main__":
    scanner = DocumentScanner()
    scanner.run()
