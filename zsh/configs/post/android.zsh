ANDROID_HOME=""
ANDROID_SDK_ROOT=""
ANDROID_AVD_HOME=""

if [ -d "$HOME/Library/Android/sdk" ]; then
    ANDROID_HOME="$HOME/Library/Android/sdk"
    ANDROID_SDK_ROOT="$ANDROID_HOME"
    ANDROID_AVD_HOME="$HOME/.android/avd"

    PATH="$ANDROID_SDK_ROOT/emulator:$ANDROID_SDK_ROOT/platform-tools:$PATH"
fi

export -U ANDROID_HOME
export -U ANDROID_SDK_ROOT
export -U ANDROID_AVD_HOME

export -U PATH
