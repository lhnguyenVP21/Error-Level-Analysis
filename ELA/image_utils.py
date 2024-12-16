from PIL import Image, ExifTags
import math

def load_image(file_path):
    try:
        image = Image.open(file_path)
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def get_exif_data(image):
    try:
        exif_data = {}
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = ExifTags.TAGS.get(tag, tag)
                exif_data[decoded] = value
        return exif_data
    except Exception as e:
        print(f"Error getting EXIF data: {e}")
        return {}

def get_camera_info(exif_data):
    camera_info = {}
    if 'Make' in exif_data:
        camera_info['Make'] = exif_data['Make']
    if 'Model' in exif_data:
        camera_info['Model'] = exif_data['Model']
    if 'LensModel' in exif_data:
        camera_info['Lens'] = exif_data['LensModel']
    return camera_info

def get_gps_info(exif_data):
    def convert_to_degrees(value):
        if value is None:
            return None
        
        degrees = float(value[0])
        minutes = float(value[1])
        seconds = float(value[2])
        
        return degrees + (minutes / 60.0) + (seconds / 3600.0)
    
    gps_info = {}
    
    if 'GPSInfo' in exif_data:
        gps_data = exif_data['GPSInfo']
        
        # Latitude
        if 1 in gps_data and 2 in gps_data:
            lat_ref = gps_data[1]
            lat = convert_to_degrees(gps_data[2])
            if lat_ref == 'S':
                lat = -lat
            gps_info['Latitude'] = lat
        
        # Longitude
        if 3 in gps_data and 4 in gps_data:
            lon_ref = gps_data[3]
            lon = convert_to_degrees(gps_data[4])
            if lon_ref == 'W':
                lon = -lon
            gps_info['Longitude'] = lon
        
        # Altitude
        if 6 in gps_data:
            alt = float(gps_data[6])
            if 5 in gps_data and gps_data[5] == 1:  # Negative altitude
                alt = -alt
            gps_info['Altitude'] = alt
    
    return gps_info

def get_dates(exif_data):
    dates = {}
    if 'DateTime' in exif_data:
        dates['Modify Date'] = exif_data['DateTime']
    if 'DateTimeOriginal' in exif_data:
        dates['Original Date'] = exif_data['DateTimeOriginal']
    if 'DateTimeDigitized' in exif_data:
        dates['Digitized Date'] = exif_data['DateTimeDigitized']
    return dates

def check_software_modify(exif_data):
    software_info = {}
    if 'Software' in exif_data:
        software_info['Software'] = exif_data['Software']
    return software_info

def format_exif_info(file_path):
    image = load_image(file_path)
    if image is None:
        return "No EXIF data available"
    
    exif_data = get_exif_data(image)
    if not exif_data:
        return "No EXIF data found"
    exif_info = []
    
    camera_info = get_camera_info(exif_data)
    if camera_info:
        exif_info.append("🎥 Camera Information:")
        for key, value in camera_info.items():
            exif_info.append(f"  - {key}: {value}")
    
    dates = get_dates(exif_data)
    if dates:
        exif_info.append("\n📅 Date Information:")
        for key, value in dates.items():
            exif_info.append(f"  - {key}: {value}")
    
    gps_info = get_gps_info(exif_data)
    if gps_info:
        exif_info.append("\n🌍 GPS Information:")
        for key, value in gps_info.items():
            exif_info.append(f"  - {key}: {value}")
    
    software_info = check_software_modify(exif_data)
    if software_info:
        exif_info.append("\n💻 Software Information:")
        for key, value in software_info.items():
            exif_info.append(f"  - {key}: {value}")
    
    return "\n".join(exif_info) if exif_info else "No significant EXIF data found"