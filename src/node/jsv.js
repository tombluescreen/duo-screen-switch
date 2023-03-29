 

const express = require("express");
var app = express();
const { exec } = require("child_process");
const http = require('http');
const { json } = require("express/lib/response");
const { exit } = require("process");

var current_screen_config = "solo";
var other_pc = "http://192.168.0.100:8080/";

function setDisplayOutput() {
    exec("ddcutil --model 27G2G3 setvcp 60 0x0f", (error, stdout, stderr) => {
        if (error) {
            console.log(`error: ${error.message}`);
            return;
        }
        if (stderr) {
            console.log(`stderr: ${stderr}`);
            return;
        }
        console.log(`stdout: ${stdout}`);
    });
}

async function getCurrentConfig() {
    //Replace with linux display manager logic
    return new Promise(resolve => {
        exec("xrandr | grep connected", (error, stdout, stderr) => {
            if (error) {
                console.log(`error: ${error.message}`);
                return;
            }
            if (stderr) {
                console.log(`stderr: ${stderr}`);
                return;
            }
            const re = /[0-9]+mm x [0-9]+mm/g;
            var m = [...stdout.matchAll(re)];
            console.log("bruh")
            if (m.length == 1) {
                resolve("solo");
            } else if (m.length == 2) {
                resolve("extended");
            }
            console.log(m)
        });
    });
    
}

function isOnCorrectNetwork() {
    //Check stages:
    //-Ping
    //-Config check
    //-Keypair check
    return true;
}

function run1Mon() {
    setDisplayOutput();
    exec("sh ../helper-scripts/linux-1-monitor.sh", (error, stdout, stderr) => {
        if (error) {
            console.log(`error: ${error.message}`);
            return;
        }
        if (stderr) {
            console.log(`stderr: ${stderr}`);
            return;
        }
        console.log(`stdout: ${stdout}`);
        
        current_screen_config = "solo";
    });
    
}

function safeRun1Mon() {
    if (isOnCorrectNetwork() == true) {
        run1Mon();
        return true;
    }
    return false;
}

function run2Mon() {
    exec("sh ../helper-scripts/linux-2-monitor.sh", (error, stdout, stderr) => {
        if (error) {
            console.log(`error: ${error.message}`);
            return;
        }
        if (stderr) {
            console.log(`stderr: ${stderr}`);
            return;
        }
        console.log(`stdout: ${stdout}`);
        current_screen_config = "extended";
    });
}

function safeRun2Mon() {
    if (isOnCorrectNetwork() == true) {
        run2Mon();
        return true;
    }
    return false;
}

app.get("/get-config", (req, res,next) => {
    getCurrentConfig().then(value => {
        console.log("Benmas")
        res.json({config: value});
    });
    
});

app.get("/set-ex", (req, res, next) => {
    res.json({comment:"not allowed"});
    return;
    var oldC = current_screen_config;
    var newC = "extended";
    var cRes = SafeRun2mon();

    if (cRes == true) {
        current_screen_config = "extended";
        
    }else if (cRes == false) {
        newC = oldC;
    }

    res.json({done: cRes, oldConfig: oldC, newConfig: newC});
});

app.get("/set-solo", (req, res, next) => {
    res.json({comment:"not allowed"});
    return;
    var oldC = current_screen_config;
    var newC = "solo";
    var cRes = SafeRun1mon();

    if (cRes == true) {
        current_screen_config = "solo";
        
    }else if (cRes == false) {
        newC = oldC;
    }
    res.json({done: cRes, oldConfig: oldC, newConfig: newC});

    
});

app.get("/get-sync", (req, res, next) => {
    getCurrentConfig().then(value => {
        console.log("Benmas")
        res.json({config: value, "hardwareSupported": false});
    });
    
});

app.get("/do-sync", (req, res, next) => {
    const query = URLSearchParams(res.url);
    

})

app.get("/switch-screen-slave", (req, res, next) => {

    

    getCurrentConfig().then(value => {
        var oldC = value;
        var newC;
        var cRes;
        if (value == "extended") {
            console.log("Screen is extended\nSwitching to solo");
            newC = "solo"
            cRes = safeRun1Mon();
        } else if (value == "solo") {
            console.log("Screen is solo\nSwitching to extended");
            newC = "extended";
            cRes = safeRun2Mon();
        }
    
        if (cRes == true) {
            current_screen_config = newC;
            
        }else if (cRes == false) {
            newC = oldC;
        }
        res.json({done: cRes, oldConfig: oldC, newConfig: newC});
    });

    
    
});

app.get("/switch-screen-host", (req, res, next) => {

    http.get(`${other_pc}switch-screen-slave`);
        getCurrentConfig().then(value => {
            var oldC = value;
            var newC;
            var cRes;
        
        if (value == "extended") {
            console.log("Screen is extended\nSwitching to solo");
            newC = "solo";
            cRes = safeRun1Mon();
        } else if (value == "solo") {
            console.log("Screen is solo\nSwitching to extended");
            newC = "extended";
            cRes = safeRun2Mon();
        }

        if (cRes == true) {
            current_screen_config = newC;
            
        }else if (cRes == false) {
            newC = oldC;
        }
        res.json({done: cRes, oldConfig: oldC, newConfig: newC});
    });
    
    
});


app.listen(8080, () => {
    console.log("Server running on port 8080");
});