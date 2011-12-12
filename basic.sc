(= util (require "util"))

(= dump (function (arglist obj)
  (var result)
  (= result (util.inspect obj false null))
  (if (== (typeof obj) "string")
    (= result (result.slice 1 (- result.length 1))))
  (console.log result)))

(= map (function (arglist func coll)
  (var result idx)
  (= result [])
  (= idx 0)
  (while (!= result.length coll.length)
    (brackets
      (result.push (func ([] coll idx)))
      (+= idx 1)))
  (return result)))

(= islist (function (arglist obj)
  (return (instanceof obj Array))))

(= list (function (arglist) 
	(var args)
	(= args (Array.prototype.slice.call arguments))
  (return args)))

(= first (function (arglist list)
  (return ([0] list))))

(= rest (function (arglist list)
  (return (list.slice 1))))

(= cons (function (arglist head tail)
  (return (head.concat tail))))
