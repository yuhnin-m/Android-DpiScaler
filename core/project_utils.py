import os

import os
import logging

def find_all_res_dirs(project_path: str):
    logging.info(f"Поиск res/ директорий в: {project_path}")
    res_dirs = []
    try:
        for root, dirs, files in os.walk(project_path):
            for d in dirs:
                if d == "res":
                    full_path = os.path.join(root, d)
                    logging.info(f"Найдена res/ директория: {full_path}")
                    res_dirs.append(full_path)
    except Exception as e:
        logging.error(f"Ошибка при поиске res/ директорий: {e}")
    logging.info(f"Всего найдено: {len(res_dirs)}")
    return res_dirs
