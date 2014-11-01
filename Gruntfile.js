

module.exports = function(grunt){
    grunt.initConfig({
        bower: {
            install: {options: {targetDir: './static/', layout: function(){ return 'lib'; }}}
        },
        jshint: {all: ['Gruntfile.js', 'index.js', 'settings.json', 'lib/*.js',
                     'templates/static/*.js']},
        uglify: {
            options: {beautify: true},
            js: {files: {
                'static/sabari.min.js': ['templates/static/sabari.js'],
                'static/ajax.min.js': ['templates/static/ajax.js'],
            }}
        },
        cssmin: {
            files: {dest: 'static/sabari.min.css', src: 'templates/static/sabari.css'}
        },
        watch: {
            options: {livereload: true},
            static: {files: ['templates/static/*'], tasks: ['uglify:js', 'cssmin']},
        },
    });
    grunt.loadNpmTasks('grunt-bower-task');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.registerTask('deploy', ['jshint', 'bower', 'uglify:js', 'cssmin']);
};
