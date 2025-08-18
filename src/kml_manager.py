import os

from models.points import PointRecord


def create_kml_file(point: PointRecord, kml_file_path: str, log_message=None) -> bool:
    """
    Создает KML файл для точки с иерархической структурой папок по дате и времени.

    Args:
        point (PointRecord): Точка для экспорта в KML.
        kml_file_path (str): Путь для сохранения KML-файла.
        log_message (callable, optional): Функция для логирования.

    Returns:
        bool: True если файл успешно создан, False при ошибке.
    """
    try:
        # Поддержка форматов '2024.11.22' и '2024-11-22'
        date_str = point.date.replace("-", ".")
        date_parts = date_str.split(".")
        time_parts = point.time.split(":")
        # Проверяем корректность даты и времени
        if len(date_parts) < 3 or len(time_parts) < 2:
            if log_message:
                log_message(f"Неверный формат даты/времени: {point.date} {point.time}", logger_level="warning", color="orange")
            return False
        day, month, year = date_parts[0], date_parts[1], date_parts[2]
        hour, minute = time_parts[0], time_parts[1]
        # Формируем содержимое KML-файла с вложенной структурой по дате
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
            <name>{point.date} {point.time} (X={int(point.x_sk42) if point.x_sk42 is not None else 'N/A'} Y={int(point.y_sk42) if point.y_sk42 is not None else 'N/A'})</name>
            <description>{point.date} {point.time}
City binding - {point.city or 'Unknown'}
Country - {point.country or 'Unknown'}
Latitude_SK42_GEO - {point.latitude:.4f}
Longitude_SK42_GEO - {point.longitude:.4f}
Latitude_SK42_Gauss_Kruger - {int(point.x_sk42) if point.x_sk42 is not None else 'N/A'}
Longitude_SK42_Gauss_Kruger - {int(point.y_sk42) if point.y_sk42 is not None else 'N/A'}</description>
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
        # Создаем директорию для файла, если нужно
        kml_dir = os.path.dirname(kml_file_path)
        if kml_dir:  # Создаем директорию только если она не пустая
            os.makedirs(kml_dir, exist_ok=True)
        # Записываем KML-файл
        with open(kml_file_path, "w", encoding="utf-8") as f:
            f.write(kml_content)
        if log_message:
            log_message(
                f"KML файл успешно создан: {kml_file_path}", logger_level="info", color="blue"
            )
        return True
    except Exception as e:
        if log_message:
            log_message(
                f"Ошибка при создании KML файла {kml_file_path}: {e}",
                logger_level="error",
                color="red",
            )
        return False
