function getFileName(e) {
    let files = e.target.files;
    console.log(files[0].name);
    console.log('{{add_video}}');

    let src = URL.createObjectURL(files[0]);

    var source = document.getElementById('file_video');
    source.setAttribute('src', src);

    var video = document.getElementById('hls-video');

    document.getElementById("video-ele").style.visibility = "visible";

    video.load();

}

function uploadFile(e) {
    loading = document.getElementById('upload-file-loading');
    loading.style.display = 'block';
    /* 3. create a new ldloader object with the newly added node */
    var ldld = new ldloader({root: "#my-loader"});
    /* 4. active this loader */
    ldld.on();
    return false;
}
