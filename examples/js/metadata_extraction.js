"use strict";
var fs = require('fs');
var path = require('path');

var testdir = '/home/develop/Downloads/MBES_data/L21_2010-10-25_post-hydrotest';

var testt = function(rootdir, findfile) {
  if(!fs.existsSync(rootdir)) {
    return console.log('Directory ' + rootdir + ' does not exist.');
  }
  
var curdir, fpath, stats;
curdir = fs.readdirSync(rootdir);
console.log(curdir );
for(var s = 0; s < curdir.length; s++) {
    //fpath = rootdir + '/' + curdir[s];
    fpath = path.join( rootdir, curdir[s]);
    stats = fs.statSync(fpath);
    
if(stats.isDirectory()) {
      testt(fpath, findfile);
    } /* else if(path.indexOf(findfile) >= 0) {
      console.log(path);
    } */
  }
};

testt(testdir, "");
