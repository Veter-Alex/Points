import os

from models.points import PointRecord
from src.logger import logger


def create_kml_file(point: PointRecord, kml_file_path: str) -> bool:
    """
    Создает KML файл для точки с иерархической структурой папок по дате и времени.
    Args:
        point: PointRecord - объект точки для создания KML
        kml_file_path: str - путь к файлу KML для сохранения
    Returns:
        bool: True если создание успешно, False если произошла ошибка
    """
    try:
        # Поддержка форматов '2024.11.22' и '2024-11-22'
        date_str = point.date.replace("-", ".")
        date_parts = date_str.split(".")
        time_parts = point.time.split(":")
        if len(date_parts) >= 3 and len(time_parts) >= 2:
            day = date_parts[0]
            month = date_parts[1]
            year = date_parts[2]
            hour = time_parts[0]
            minute = time_parts[1]
        else:
            logger.warning(f"Неверный формат даты/времени: {point.date} {point.time}")
            return False
        kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
  <Document>
    <Folder>
      <name>{year}</name>
      <open>1</open>
      <Style>
        <ListStyle>
          <listItemType>check</listItemType>
          <bgColor>00ffffff</bgColor>
        </ListStyle>
      </Style>
      <Folder>
        <name>{month}</name>
        <open>1</open>
        <Style>
          <ListStyle>
            <listItemType>check</listItemType>
            <bgColor>00ffffff</bgColor>
          </ListStyle>
        </Style>
        <Folder>
          <name>{day}</name>
          <open>1</open>
          <Style>
            <ListStyle>
              <listItemType>check</listItemType>
              <bgColor>00ffffff</bgColor>
            </ListStyle>
          </Style>
          <Placemark>
            <name>{point.date} {point.time} (X={point.x_sk42 or 'N/A'} Y={point.y_sk42 or 'N/A'})</name>
            <description>{point.date} {point.time}
City binding - {point.city or 'Unknown'}
Country - {point.country or 'Unknown'}
Latitude_SK42_GEO - {point.latitude:.4f}
Longitude_SK42_GEO - {point.longitude:.4f}
Latitude_SK42_Gauss_Kruger - {point.x_sk42 or 'N/A'}
Longitude_SK42_Gauss_Kruger - {point.y_sk42 or 'N/A'}</description>
            <Style>
              <LabelStyle>
                <color>FF00FFFF</color>
                <scale>1.09090909090909</scale>
              </LabelStyle>
              <IconStyle>
                <scale>0.390625</scale>
                <Icon>
                  <href>files/1.png</href>
                </Icon>
                <hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
              </IconStyle>
            </Style>
            <Point>
              <extrude>1</extrude>
              <coordinates>{point.longitude:.8f},{point.latitude:.8f},0</coordinates>
            </Point>
          </Placemark>
        </Folder>
      </Folder>
    </Folder>
  </Document>
</kml>
"""
        os.makedirs(os.path.dirname(kml_file_path), exist_ok=True)
        with open(kml_file_path, "w", encoding="utf-8") as f:
            f.write(kml_content)
        logger.info(f"KML файл успешно создан: {kml_file_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании KML файла {kml_file_path}: {e}")
        return False
