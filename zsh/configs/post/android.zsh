ANDROID_HOME=""
ANDROID_USER_HOME=""

ANDROID_SDK_ROOT=""
ANDROID_AVD_HOME=""

if [ -d "$HOME/Library/Android/sdk" ]; then
    ANDROID_HOME="$HOME/Library/Android/sdk"
    ANDROID_SDK_ROOT="$ANDROID_HOME"

    ANDROID_USER_HOME="$HOME/.android"
    ANDROID_AVD_HOME="$ANDROID_USER_HOME/avd"

    PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$PATH"
fi

export -U ANDROID_HOME
export -U ANDROID_SDK_ROOT
export -U ANDROID_AVD_HOME

export -U PATH
