#!/usr/bin/python
import re
import sys
import subprocess

DEBUG = (sys.argv[2] == "--macro")
input = "\n".join([l for l in open(sys.argv[1])])

# Evaluate str with node.
def nodejs(str):
  open("temp", 'w').write(header + str)
  return subprocess.check_output(["node", "temp"])

array_to_scheme = """
function to_scheme(item){
  if (!(item instanceof Array)) {
    return item;
  }
  var result = "(";
  for (var i = 0; i < item.length; i++){
    result += to_scheme(item[i]) + (i == item.length - 1 ? "" : " ");
  }
  result += ")";
  return result;
}
"""

def toscheme(str):
  return nodejs(array_to_scheme + "dump(to_scheme(%s));" % str)

class Node:
  known_macros = []
  macro_js = ""

  def __init__(self, name, args):
    assert isinstance(args, list)
    self.name = name
    self.args = args
  
  # Return scheme representation of self. This is exactly the same as what
  # we read in from the file.
  def toscheme(self):
    return "(%s " % self.name + " ".join([arg.toscheme() for arg in self.args]) + ")"

  def tostr(self, indent):
    indentation = indent * "  "
    result = ""

    result = indentation + self.name
    for arg in self.args:
      result += "\n" + arg.tostr(indent + 1)

    return result

  def __repr__(self):
    return self.tostr(0)

  # Preliminary pass to compile all macros into JS.
  def compile_macro(self):
    if self.name == "defmacro":
      Node.known_macros.append(self.args[0].compile())
      return "\nfunction %s %s { %s } \n" % (self.args[0].compile(), self.args[1].compile(), self.args[2].compile())
    return "".join([arg.compile_macro() for arg in self.args])
  
  # This pass converts all calls to macros into the resultant forms.
  def first_pass(self):
    if self.name in Node.known_macros or (self.name == "call" and self.args[0].compile() in Node.known_macros):
      if DEBUG: print "Transforming %s\n\n" % (self.toscheme())
      macro_name = self.name if self.name in Node.known_macros else self.args[0].compile()
      # Construct JavaScript to call JS function and pass in args
      # TODO: This will be wrong if I get rid of call.
      js = "dump(" + macro_name + "(" + ",".join([repr(arg.toscheme()) for arg in self.args[1:]]) + "))"
      result = nodejs(Node.macro_js + js)
      # Result is now basically what we want, except it's JavaScript arrays.
      result = toscheme(result)
      new_node = parse(result, False)
      self.args = new_node.args
      self.name = new_node.name
      if DEBUG: print "Transformed to %s\n-----------" % (self.toscheme())
      return

    for node in self.args:
      node.first_pass()
  
  def compile(self):
    ops = ["+", "/", "*", "-", "||", "&&", "===", "!==", "!=", "==", "+=", "-=", "/=", "*=", "instanceof", "<", ">", "<=", ">=", "%"]
    unary = ["!", "+", "-", "new", "typeof", "++", "--"]

    name = self.name
    if name == "=":
      return "%s = %s" % (self.args[0].compile(), self.args[1].compile())
    elif name == "parenthesize":
      return "(%s)" % (self.args[0].compile())
    elif name == "brackets":
      return "{%s}" % (";\n".join([arg.compile() for arg in self.args]))
    elif name == "root":
      return ";\n".join([arg.compile() for arg in self.args])
    elif name == "break":
      return "break;"
    elif name == "continue":
      return "continue"
    elif name == "defmacro":
      return ""
    elif name == "call":
      if len(self.args) == 1:
        return "%s()" % (self.args[0].compile())
      return "%s(%s)" % (self.args[0].compile(), ", ".join([arg.compile() for arg in self.args[1:]]))
    elif name == "try":
      return "try {\n%s\n} catch %s  {\n%s} finally {\n%s}" % (self.args[0].compile(), self.args[1].compile(), self.args[2].compile(), self.args[3].compile())
    elif name == "do":
      if len(self.args) == 0:
        return "(void 0)"
      return ";\n".join([arg.compile() for arg in self.args])
    elif name == "docomma":
      assert len(self.args) > 0
      return ",\n".join([arg.compile() for arg in self.args])
    elif name == "var":
      return "var %s" % ",".join([arg.compile() for arg in self.args])
    elif name == "[]":
      return "%s[%s]" % (self.args[0].compile(), self.args[1].compile())
    elif name == "[0]": #TODO: Remove for "[]"
      return "(%s)[0]" % self.args[0].compile()
    elif name == "root":
      return ";\n".join([arg.compile() for arg in self.args])
    elif name == "==":
      return "%s == %s" % (self.args[0].compile(), self.args[1].compile())
    elif name == "while":
      return "while (%s) %s;" % (self.args[0].compile(), self.args[1].compile())
    elif name == "if":
      while len(self.args) < 3:
        self.args.append(Node("void", [Atom("0")])) # Append empty bodies to unfilled parts of the if
      
      return "if (%s) {%s;} else {%s;}" % (self.args[0].compile(), self.args[1].compile(), self.args[2].compile())
    elif name == "ternary":
      return "%s ? %s : %s " % (self.args[0].compile(), self.args[1].compile(), self.args[2].compile())
      # return ("if (%s) {%s;} else {%s;}") % (self.args[0].compile(), self.args[1].compile(), self.args[2].compile())
    elif name == "function":
      return "function %s { %s }" % (self.args[0].compile(), ";".join([arg.compile() for arg in self.args[1:]]))
    elif name == "arglist":
      return "(" + ",".join([arg.compile() for arg in self.args]) + ")"

    for op in ops:
      if name == op and len(self.args) > 2:
        expr = (" " + op + " ").join([arg.compile() for arg in self.args if arg.compile().strip() != ""])
        return "(" + expr + ")"
      
      if name == op and len(self.args) == 2:
        return "(%s %s %s)" % (self.args[0].compile(), op, self.args[1].compile())
    
    for op in unary:
      if name == op and len(self.args) == 1:
        return "(%s %s)" % (op, self.args[0].compile())

    # A special case for stuff like ((function (arglist) 5))
    # where you immediately call an anonymous function.
    if self.name == "":
      return "(%s)()" % self.args[0].compile()
    else:
      return "%s(%s)" % (self.name, ", ".join([arg.compile() for arg in self.args]))


class Atom:
  def __init__(self, contents):
    self.contents = contents

  def tostr(self, indent):
    return indent * "  " + self.contents

  def toscheme(self):
    return self.contents
  
  def compile(self):
    return self.contents
  
  def first_pass(self):
    pass
  
  def compile_macro(self):
    return ""
 
  def __repr__(self):
    return "Atom " + self.contents

def is_paren(str):
  return str == "(" or str == ")"

# Add quoting functionality: some basic syntactic sugar to make
# writing macros easier on the eyes (and brain...)
def desugar(tokens):
  result = []
  quoted = False
  depth = 0
  for token in tokens:
    if token == "`(":
      quoted = True
      result.append("(")
      result.append("list")
      depth = 1
    elif token == "(":
      result.append(token)
      if quoted: result.append("list")
      depth += 1
    elif token == ")":
      result.append(token)
      depth -= 1
      if depth == 0 and quoted:
        quoted = False
    elif token[0] == "~":
      if not quoted:
        raise "Unquote in nonquoted form?"
      result.append(token[1:]) #remove tilde, keep token.
    else:
      result.append('"%s"' % token if quoted else token)
  
  return result

def tokenize(string):
  in_string = False
  string_opener = ""
  tokens = [""]
  for ch in string:
    if (ch == "'" or ch == '"') and (string_opener == ch or string_opener == ""):
      string_opener = (ch if string_opener == "" else "")
       
      in_string = not in_string
      tokens[-1] += ch
      if not in_string: tokens.append("")
      continue

    if not in_string:
      if ch == " ":
        tokens.append("")
        continue

      if is_paren(ch):
        if tokens[-1] == "`": # Special case for quoted parens.
          tokens[-1] += ch
        else:
          tokens.append(ch)
        tokens.append("")
        continue

    tokens[-1] += ch
      
  tokens = [tok.strip() for tok in tokens[:-1] if tok.strip() != ""]
  tokens = desugar(tokens)
  return tokens

def parse(string, root=True):
  string = string.strip()
  if root: string = "(root " + string + ")"
  tokens = tokenize(string)

  def helper(tokens):
    node_name = tokens[1]
    node_args = [[]]
    # If we immediately call a function, make it an arg of a 
    # special cased function with no name.
    if node_name == "(":
      node_name = ""
      tokens = tokens[1:-1]
    else:
      tokens = tokens[2:-1] #ignore (, name, and ).

    depth = 0
    for token in tokens:
      if is_paren(token): 
        depth = depth + (1 if token == "(" else -1)
        node_args[-1].append(token)

        if depth == 0: 
          node_args[-1] = helper(node_args[-1])
          node_args.append([])
        continue

      if depth == 0:
        node_args[-1] = Atom(token)
        node_args.append([])
      else:
        node_args[-1].append(token)

    node_args = node_args[:-1]
    return Node(node_name, node_args)
  
  return helper(tokens)

ast = parse(input)

output = sys.argv[1].split(".")[0] + ".js" #same name as input, but .js instead of .sc

# Header contains some basic lisp-y functions.
header = "".join([line for line in file("basic.sc")]) + "\n"
header = parse(header).compile()

Node.macro_js = ast.compile_macro()

ast.first_pass()
if sys.argv[2] == "--macro":
  open("macropass", "w").write(ast.toscheme())

open(output, 'w').write(ast.compile())
