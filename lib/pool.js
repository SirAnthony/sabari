
function Pool(){
    var max_running = 30
    var running = 0
    var timer = null
    var timeout = 4
    var pool = []

    function resolver(err, data){
        running--
        process.nextTick(run)
        return err, data
    }

    function run(){
        if (pool.length <= 0)
            return
    	if (running > max_running)
            return process.nextTick(run)
    	for (var i=running; i<max_running; ++i){
            var callback = pool.shift()
            if (!callback)
                return
            running++
            callback(resolver)
    	}
    }

    this.add = function(callback){
        pool.push(callback)
        process.nextTick(run)
    }
}

exports.Pool = new Pool()

