

module.exports = function(grunt){
    grunt.initConfig({
        bower: {
            install: {options: {targetDir: './static/'}}
        },
        uglify: {
            files: {'static/sabari.min.js': ['templates/static/sabari.js'],}
        },
        cssmin: {
            files: {dest: 'static/sabari.min.css', src: 'templates/static/sabari.css'}
        },
        watch: {files: ['templates/static/*'], tasks: ['uglify', 'cssmin']},
    })
    grunt.loadNpmTasks('grunt-bower-task');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.registerTask('deploy', ['bower', 'uglify', 'cssmin']);
}
