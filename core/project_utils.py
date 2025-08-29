import logging
import os


def find_all_res_dirs(project_path: str):
    logging.info(f"Поиск res/ директорий в: {project_path}")
    res_dirs = []

    try:
        for root, dirs, _files in os.walk(project_path):
            for directory in dirs:
                if directory == "res":
                    full_path = os.path.join(root, directory)

                    normalized = os.path.normpath(full_path)
                    parts = normalized.split(os.sep)

                    if "build" in parts:
                        build_index = parts.index("build")
                        if build_index + 1 < len(parts) and parts[build_index + 1] == "generated":
                            logging.info(f"Пропущено (build/generated): {full_path}")
                            continue

                    res_dirs.append(full_path)
                    logging.info(f"Найдена res/ директория: {full_path}")
    except Exception as error:
        logging.error(f"Ошибка при поиске res/ директорий: {error}")

    logging.info(f"Всего найдено: {len(res_dirs)}")
    return res_dirs
