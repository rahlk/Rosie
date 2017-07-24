function codebotBootstrap(theAppConfig) {
    var aIsNodeWebkit, aIsChromeApp;

    console.log('CODEBOT [bootstrap] App configuration file (app.json):', theAppConfig);

    if(theAppConfig && theAppConfig.bootstrap) {
        // App config file tells us to use a custom-made bootstrapper.
        // So be it!
        console.log('CODEBOT [bootstrap] Firing up custom bootstrapper: ' + theAppConfig.bootstrap);
        $('body').append('<script type="text/javascript" src="'+theAppConfig.bootstrap+'"></script>');

    } else {
        aIsNodeWebkit = 'require' in window;
        aIsChromeApp  = false; // TODO: check it correctly.

        if(aIsNodeWebkit) {
            console.log('CODEBOT [bootstrap] Node-webkit app.');
            $('body').append('<script type="text/javascript" src="./js/node-webkit/codebot.bootstrap.nw.js"></script>');

        } else if(aIsChromeApp) {
            console.log('CODEBOT [bootstrap] Chrome Packaged App.');

        } else {
            // It's running in the browser.
            console.log('CODEBOT [bootstrap] Browser app');
            $('body').append('<script type="text/javascript" src="./js/web/codebot.bootstrap.web.js"></script>');
        }
    }
}

// Wait until the DOM is ready, then starts loading
// the app configuration file.

$(function() {
    $.getJSON('./app.json')
    .done(function(theData) {
        if(theData.codebot) {
            codebotBootstrap(theData.codebot);

        } else {
            console.error('Codebot app.json file has no "codebot" property. E.g. {"codebot": {...}}.');
        }
    })
    .fail(function(theJqxhr, theTextStatus, theError) {
        if(theJqxhr.status == 404) {
            codebotBootstrap(null);

        } else {
            // Probably a syntax error.
            console.error('Codebot app.json file has a sintax error:', theTextStatus, theError);
        }
    });
});