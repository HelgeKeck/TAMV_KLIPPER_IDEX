# Prevent running as root.
if [ ${UID} == 0 ]; then
    echo -e "DO NOT RUN THIS SCRIPT AS 'root' !"
    echo -e "If 'root' privileges needed, you will prompted for sudo password."
    exit 1
fi

# Force script to exit if an error occurs
set -e

# Find SRCDIR from the pathname of this script
SRCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/ && pwd )"

# Default Parameters
KLIPPER_CONFIG_DIR="${HOME}/klipper_config"
PRINTER_DATA_CONFIG_DIR="${HOME}/printer_data/config"
KLIPPY_EXTRAS="${HOME}/klipper/klippy/extras"

function get_config_dir {
    if [ -d "${PRINTER_DATA_CONFIG_DIR}" ]; then
        echo -e "Installing into printer data config dir."
        CONFIG_DIR="${PRINTER_DATA_CONFIG_DIR}"
    else
        if [ -d "${KLIPPER_CONFIG_DIR}" ]; then
            echo -e "Installing into klipper config dir."
            CONFIG_DIR="${KLIPPER_CONFIG_DIR}"
        else
            echo -e "ERROR: No RatOS config folder found."
            exit 1
        fi
    fi
}

function start_klipper {
    sudo systemctl restart klipper
}

function stop_klipper {
    if [ "$(sudo systemctl list-units --full -all -t service --no-legend | grep -F "klipper.service")" ]; then
        sudo systemctl stop klipper
    else
        echo "Klipper service not found, please install Klipper first"
        exit 1
    fi
}

function link_klippy_extension {
    if [ -d "${KLIPPY_EXTRAS}" ]; then
        rm -f "${KLIPPY_EXTRAS}/tamv.py"
        ln -sf "${SRCDIR}/klippy_extra/tamv.py" "${KLIPPY_EXTRAS}/tamv.py"
    else
        echo -e "ERROR: ${KLIPPY_EXTRAS} not found."
        exit 1
    fi
}

stop_klipper
get_config_dir
link_klippy_extension
start_klipper

exit 0
