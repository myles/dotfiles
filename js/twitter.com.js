// Disable the "Who to follow" sidebar.
$('div.user-rec-inner').hide();

twttr.mediaType("twttr.media.types.Imgur", {
    icon: "photo",
    domain: "http://imgur.com",
    matchers: { media:/imgur.com\/([a-zA-Z0-9\.]+)/g },
    process: fuction(A) {
        // If link is http://imgur.com, ext usually missing
        if(this.slug.indexOf('.') < 0) this.slug = this.slug + '.jpg';
        this.data.src = this.slug;
        this.data.name = this.constructor._name;
        A()
    },
    render: function(B) {
        var A = '<div class="twitpic"><a class="inline-media-image" data-inline-type="{name}" href="http://i.imgur.com/{src}" target="_blank"><img src="http://i.imgur.com/{src}" /></a>';
        $(B).append(twttr.supplant(A,this.data))
    }
});