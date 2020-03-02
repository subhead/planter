#!/usr/bin/env bash
# shellcheck disable=SC1090

# Install with this command (from your Linux machine):
#
# curl -sSL https://raw.githubusercontent.com/subhead/planter/master/install.sh | bash

# -e option instructs bash to immediately exit if any command [1] has a non-zero exit status
# We do not want users to end up with a partially working install, so we exit the script
# instead of continuing the installation with something broken
set -e

PLANTER_GIT_URL='https://github.com/subhead/planter.git'
PLANTER_LOCAL_REPO='/etc/.planter'
PLANTER_INSTALL_DIR='/opt/planter'
PLANTER_LOG_DIR='/opt/planter/log'
PLANTER_DATA_DIR='/opt/planter/data'
PLANTER_DB_DIR='/opt/planter/data/db'
PLANTER_IMAGE_DIR='/opt/planter/data/images'
PLANTER_LOG_FILE='planter.log'
PLANTER_FILES=("$PLANTER_LOCAL_REPO"/app/{planter.py,requirements.txt,settings.toml,docker-compose.yml,dashboard.yml,dashboard/})

# Set these values so the installer can still run in color
COL_NC='\e[0m' # No Color
COL_LIGHT_GREEN='\e[1;32m'
COL_LIGHT_RED='\e[1;31m'
COL_BROWN='\e[1;33m'
TICK="[${COL_LIGHT_GREEN}✓${COL_NC}]"
CROSS="[${COL_LIGHT_RED}✗${COL_NC}]"
INFO="[i]"
# shellcheck disable=SC2034
DONE="${COL_LIGHT_GREEN} done!${COL_NC}"
OVER="\\r\\033[K"

if [ -z "${USER}" ]; then
  USER="$(id -un)"
fi

# Check if we are running on a real terminal and find the rows and columns
# If there is no real terminal, we will default to 80x24
if [ -t 0 ] ; then
  screen_size=$(stty size)
else
  screen_size="24 80"
fi
# Set rows variable to contain first number
printf -v rows '%d' "${screen_size%% *}"
# Set columns variable to contain second number
printf -v columns '%d' "${screen_size##* }"

# Divide by two so the dialogs take up half of the screen, which looks nice.
r=$(( rows / 2 ))
c=$(( columns / 2 ))
# Unless the screen is tiny
r=$(( r < 20 ? 20 : r ))
c=$(( c < 70 ? 70 : c ))

show_planter_ascii() {
  echo -e "
                    ${COL_LIGHT_GREEN}///                          
                  //////                         
                *//*///                         
    ///////     ,/////*                         
      ////////    / //     ////*                 
        ///////        /////////,                
          *//*/ .*  /////////*                  
                *                               
                  /                              
                  /                             
        ${COL_BROWN}*/////////////////////*                   
        */////////////////////*                  
        */////////////////////*                    
         *///////////////////*                    
           /////////////////                     
            ///////////////                     
             /////////////${COL_NC}                      
          "
}

is_command() {
    # Checks for existence of string passed in as only function argument.
    # Exit value of 0 when exists, 1 if not exists. Value is the result
    # of the `command` shell built-in call.
    local check_command="$1"
    command -v "${check_command}" >/dev/null 2>&1
}

check_distro() {
  if grep -qiE 'raspbian|debian|ubuntu' /etc/os-release; then
    DISTRO_NAME=$(grep -iE '^name' /etc/os-release | awk 'BEGIN { FS = "\"" } ; { print $2 }')
    DISTRO_CHECK=true
  fi
}

check_raspi() {
	if grep -qiE 'raspberry' /proc/device-tree/model; then
    RASPI_MODEL=$(cat /proc/device-tree/model | tr -d "\r\n\0")
		RASPI_CHECK=true
	fi
}

check_git() {
  if ! is_command git; then
    GIT_CHECK=true
  fi
}

check_curl() {
  if is_command curl; then
    CURL_CHECK=true
  fi
}

check_pkg_manager() {
  if is_command apt-get; then
    PKG_MANAGER="apt-get"
    PKG_MANAGER_PATH=$(command -v apt-get)
    # A variable to store the command used to update the package cache
    PKG_MANAGER_CHECK=true
  fi
}

pkg_prepare() {
  local PKG_MANAGER="${1}" 
  if ! is_command curl ; then
    "${PKG_MANAGER}" update -y
    "${PKG_MANAGER}" install -y curl git python3 python3-dev python3-pip python3-setuptools python3-venv postgresql-server-dev-all
  else
    "${PKG_MANAGER}" install -y git python3 python3-dev python3-pip python3-setuptools python3-venv 
  fi
}

pgk_docker_install() {
  curl https://get.docker.com | sh
}

pkg_docker_compose_install() {
  local PKG_MANAGER="${1}"
  "${PKG_MANAGER}" install -y libssl-dev libffi-dev
  python3 -m pip install -IU docker-compose
}

check_webcam() {
  if [ -c /dev/video0 ]; then
    WEBCAM_CHECK=true
    WEBCAM_DEVICE=/dev/video0
  fi
}

check_gpio() {
  if [ -d /sys/class/gpio/gpiochip0 ]; then
    GPIO_CHECK=true
    GPIO_PATH=/sys/class/gpio/
  fi
}

check_wiringpi() {
  if ! is_command gpio; then
    WIRINGPI_CHECK=false
  else
    WIRINGPI_CHECK=true
  fi
}

install_wiringpi() {
  #local PKG_MANAGER="${1}"
  #"${PKG_MANAGER}" install wiringpi
  cd /tmp
  wget https://project-downloads.drogon.net/wiringpi-latest.deb
  sudo dpkg -i /tmp/wiringpi-latest.deb
}

check_docker() {
  if is_command docker; then
    DOCKER_CHECK=true
    DOCKER_PATH=$(command -v docker)
  fi
}

check_docker_compose() {
  if is_command docker-compose; then
    DOCKER_COMPOSE_CHECK=true
    DOCKER_COMPOSE_PATH=$(command -v docker-compose)
  fi
}

is_repo() {
    # Use a named, local variable instead of the vague $1, which is the first argument passed to this function
    # These local variables should always be lowercase
    local directory="${1}"
    # A local variable for the current directory
    local curdir
    # A variable to store the return code
    local rc
    # Assign the current directory variable by using pwd
    curdir="${PWD}"
    # If the first argument passed to this function is a directory,
    if [[ -d "${directory}" ]]; then
        # move into the directory
        cd "${directory}"
        # Use git to check if the directory is a repo
        # git -C is not used here to support git versions older than 1.8.4
        git status --short &> /dev/null || rc=$?
    # If the command was not successful,
    else
        # Set a non-zero return code if directory does not exist
        rc=1
    fi
    # Move back into the directory the user started in
    cd "${curdir}"
    # Return the code; if one is not set, return 0
    return "${rc:-0}"
}

# A function to clone a repo
make_repo() {
    # Set named variables for better readability
    local directory="${1}"
    local remoteRepo="${2}"
    # The message to display when this function is running
    str="Clone ${remoteRepo} into ${directory}"
    # Display the message and use the color table to preface the message with an "info" indicator
    printf "  %b %s..." "${INFO}" "${str}"
    # If the directory exists,
    if [[ -d "${directory}" ]]; then
        # delete everything in it so git can clone into it
        rm -rf "${directory}"
    fi

    printf "\n${remoteRepo}\n"
    printf "${directory}\n"
    # Clone the repo and return the return code from this command
    git clone -q --depth 20 "${remoteRepo}" "${directory}" &> /dev/null || return $?
    # Show a colored message showing it's status
    printf "%b  %b %s\\n" "${OVER}" "${TICK}" "${str}"
    # Always return 0? Not sure this is correct
    return 0
}

# We need to make sure the repos are up-to-date so we can effectively install Clean out the directory if it exists for git to clone into
update_repo() {

    local directory="${1}"
    local curdir

    # A variable to store the message we want to display;
    local str="Update repo in ${1}"

    # Make sure we know what directory we are in so we can move back into it
    curdir="${PWD}"
    # Move into the directory that was passed as an argument
    cd "${directory}" &> /dev/null || return 1
    # Let the user know what's happening
    printf "  %b %s..." "${INFO}" "${str}"
    # Stash any local commits as they conflict with our working code
    git stash --all --quiet &> /dev/null || true # Okay for stash failure
    git clean --quiet --force -d || true # Okay for already clean directory
    # Pull the latest commits
    git pull --quiet &> /dev/null || return $?
    # Show a completion message
    printf "%b  %b %s\\n" "${OVER}" "${TICK}" "${str}"
    # Move back into the original directory
    cd "${curdir}" &> /dev/null || return 1
    return 0
}

# A function that combines the functions previously made
getGitFiles() {
    # Setup named variables for the git repos
    # We need the directory
    local directory="${1}"
    # as well as the repo URL
    local remoteRepo="${2}"
    # A local variable containing the message to be displayed
    local str="Check for existing repository in ${1}"
    # Show the message
    printf "  %b %s..." "${INFO}" "${str}"
    # Check if the directory is a repository
    if is_repo "${directory}"; then
        printf "la"
        # Show that we're checking it
        printf "%b  %b %s\\n" "${OVER}" "${TICK}" "${str}"
        # Update the repo, returning an error message on failure
        update_repo "${directory}" || { printf "\\n  %b: Could not update local repository.%b\\n" "${COL_LIGHT_RED}" "${COL_NC}"; exit 1; }
    # If it's not a .git repo,
    else
        printf "le"
        mkdir -p "${directory}"
        # Show an error
        printf "%b  %b %s\\n" "${OVER}" "${CROSS}" "${str}"
        # Attempt to make the repository, showing an error on failure
        make_repo "${directory}" "${remoteRepo}" || { printf "\\n  %bError: Could not update local repositoryy.%b\\n" "${COL_LIGHT_RED}" "${COL_NC}"; exit 1; }
    fi
    # echo a blank line
    echo ""
    # and return success?
    return 0
}


main() {

  show_planter_ascii

	printf "Starting Planter bootstrap script.\n"

  # Must be root to install
  local str="Root user check"
  printf "\\n"
  # If the user's id is zero,
  if [[ "${EUID}" -eq 0 ]]; then
      # they are root and all is good
      printf "  %b %s\\n" "${TICK}" "${str}"
  else
      printf "  %b %s\\n" "${CROSS}" "${str}"
      printf "  %b %bScript called with non-root privileges%b\\n" "${INFO}" "${COL_LIGHT_RED}" "${COL_NC}"
  fi

  printf "  %b %s\n" "${INFO}" "Checking the environment"
  
  check_raspi
  # Check the platform, exit if not a Raspberry Pi
  if [[ "${RASPI_CHECK}" == true ]]; then
    printf "  %b Raspberry Pi found (%s)\n" "${TICK}" "${RASPI_MODEL}"
  else
    printf "  %b %s\n" "${CROSS}" "No Rasperry Pi found. Exiting."
    exit 3
  fi

  check_distro
  # Check the distro, exit if not a debian based
  if [[ "${DISTRO_CHECK}" == true ]]; then
    printf "  %b Debian flavored distribution found (%s)\n" "${TICK}" "${DISTRO_NAME}"
  else
    printf "  %b %s\n" "${CROSS}" "No Debian flavored distribution found. Exiting"
    exit 3
  fi

  check_pkg_manager
  # Check if the package manager is apt/apt-get
  if [[ "${PKG_MANAGER_CHECK}" == true ]]; then
    printf "  %b Package manager found (%s)\n" "${TICK}" "${PKG_MANAGER_PATH}"
  else
    printf "  %b %s\n" "${CROSS}" "Not a valid package manager found. Exiting."
    exit 3
  fi

  check_gpio
  # Check if a gpio is present
  if [[ "${GPIO_CHECK}" == true ]]; then
    printf "  %b GPIO found (%s)\n" "${TICK}" "${GPIO_PATH}"
    
    check_wiringpi
    if [[ "${WIRINGPI_CHECK}" == false ]]; then
      printf "  %b WiringPi not found. Flagging for installation.\n" "${CROSS}"
      INSTALL_WIRINGPI=true
    fi

  else
    printf "  %b %s\n" "${CROSS}" "No GPIO detected."
  fi

  check_webcam
  # Check if a webcam is attached
  if [[ "${WEBCAM_CHECK}" == true ]]; then
    printf "  %b Webcam found (%s)\n" "${TICK}" "${WEBCAM_DEVICE}"
  else
    printf "  %b %s\n" "${CROSS}" "No webcam detected."
  fi

  check_docker
  # Check if a webcam is attached
  if [[ "${DOCKER_CHECK}" == true ]]; then
    printf "  %b Docker found (%s)\n" "${TICK}" "${DOCKER_PATH}"
  else
    printf "  %b %s\n" "${CROSS}" "Docker not found. Flagging for installation."
    INSTALL_DOCKER=true
  fi

  check_docker_compose
  # Check if a webcam is attached
  if [[ "${DOCKER_COMPOSE_CHECK}" == true ]]; then
    printf "  %b docker-compose found (%s)\n" "${TICK}" "${DOCKER_COMPOSE_PATH}"
  else
    printf "  %b %s\n" "${CROSS}" "docker-compose not found. Flagging for installation"
    INSTALL_DOCKER_COMPOSE=true
  fi  

  printf "  %b %s\n" "${INFO}" "The environment have passed all checks."
  printf "  %b %s\n" "${INFO}" "Starting the installation of Planter."
  
  #printf "\n"
  #read -p "  Press enter to continue or strg-c to cancel the installation"
  printf "\n"

  pkg_prepare "${PKG_MANAGER}"

  if [[ "${INSTALL_WIRINGPI}" == true ]]; then
    install_wiringpi
  fi

  if [[ "${INSTALL_DOCKER}" == true ]]; then
    pgk_docker_install
  fi

  if [[ "${INSTALL_DOCKER_COMPOSE}" == true ]]; then
    pkg_docker_compose_install "${PKG_MANAGER}"
  fi

  # Checkout planter
  getGitFiles "${PLANTER_LOCAL_REPO}" "${PLANTER_GIT_URL}" || \
  { printf "  %bUnable to clone %s into %s, unable to continue%b\\n" "${COL_LIGHT_RED}" "${PLANTER_GIT_URL}" "${PLANTER_LOCAL_REPO}" "${COL_NC}"; \
  exit 1; \
  }

  # make directories
  mkdir -p "${PLANTER_INSTALL_DIR}"
  mkdir -p "${PLANTER_LOG_DIR}"
  mkdir -p "${PLANTER_DATA_DIR}"
  mkdir -p "${PLANTER_DB_DIR}"
  mkdir -p "${PLANTER_IMAGE_DIR}"

  # install planter
  cp ${PLANTER_FILES[@]} "${PLANTER_INSTALL_DIR}"


  printf "  %b %s\n" "${TICK}" "Installation completed."
}

# Let´s start with the installation
if [[ "${PLANTER_TEST}" != true ]] ; then
    main "$@"
fi