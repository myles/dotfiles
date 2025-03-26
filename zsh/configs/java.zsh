JAVA_HOME=""

if [ -d "/Library/Java/JavaVirtualMachines/zulu-17.jdk/Contents/Home" ]; then
    JAVA_HOME=/Library/Java/JavaVirtualMachines/zulu-17.jdk/Contents/Home

    PATH="$JAVA_HOME/bin:$PATH"
fi

export -U JAVA_HOME

export -U PATH
