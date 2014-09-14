

module.exports = function(grunt){
    grunt.initConfig({
        bower: {
            install: {options: {targetDir: './static/', layout: function(){ return 'lib' }}}
        },
        uglify: {
            options: {beautify: true},
            js: {files: {'static/sabari.min.js': ['templates/static/sabari.js']}}
        },
        cssmin: {
            files: {dest: 'static/sabari.min.css', src: 'templates/static/sabari.css'}
        },
        watch: {
            options: {livereload: true},
            static: {files: ['templates/static/*'], tasks: ['uglify:js', 'cssmin']},
        },
    })
    grunt.loadNpmTasks('grunt-bower-task')
    grunt.loadNpmTasks('grunt-contrib-uglify')
    grunt.loadNpmTasks('grunt-contrib-cssmin')
    grunt.loadNpmTasks('grunt-contrib-watch')
    grunt.registerTask('deploy', ['bower', 'uglify:js', 'cssmin'])
}
