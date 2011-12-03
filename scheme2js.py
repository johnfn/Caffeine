#!/usr/bin/python
import re
import sys

input = "\n".join([l for l in open(sys.argv[1])])

class Node:
  def __init__(self, name, args):
    assert isinstance(args, list)
    self.name = name
    self.args = args

  def tostr(self, indent):
    indentation = indent * "  "
    result = ""

    result = indentation + self.name
    for arg in self.args:
      result += "\n" + arg.tostr(indent + 1)

    return result

  def __repr__(self):
    return self.tostr(0)

  def wrap(self, str):
    return "(function(){return %s;})()" % (str)
  
  def compile(self):
    name = self.name
    if name == "=":
      return "%s = %s" % (self.args[0].compile(), self.args[1].compile())
    elif name == "call":
      return "(%s)()" % self.args[0].compile()
    elif name == "do":
      return ";\n".join([arg.compile() for arg in self.args])
    elif name == "var":
      return "var %s" % ",".join([arg.compile() for arg in self.args])
    elif name == "root":
      return ";\n".join([arg.compile() for arg in self.args])
    elif name == "==":
      return "%s == %s" % (self.args[0].compile(), self.args[1].compile())
    elif name == "if":
      return ("if (%s) {%s;} else {%s;}") % (self.args[0].compile(), self.args[1].compile(), self.args[2].compile())
    elif name == "fn":
      return "function %s { %s }" % (self.args[0].compile(), ";".join([arg.compile() for arg in self.args[1:]]))
    elif name == "arglist":
      return "(" + ",".join([arg.compile() for arg in self.args]) + ")"
    elif name == "+":
      return "(%s + %s)" % (self.args[0].compile(), self.args[1].compile())
    else: #unknown function name, translate to js directly
      return "%s(%s)" % (self.name, ", ".join([arg.compile() for arg in self.args]))


class Atom:
  def __init__(self, contents):
    self.contents = contents

  def tostr(self, indent):
    return indent * "  " + self.contents

  def compile(self):
    return self.contents
 
  def __repr__(self):
    return "Atom " + self.contents

def tokenize(string):
  string = string.replace("(", " ( ")
  string = string.replace(")", " ) ")
  return [token.strip() for token in string.split(" ") if token.strip() != ""]

def parse(string):
  string = string.strip()
  string = "(root " + string + ")"
  tokens = tokenize(string)

  def paren(str):
    return str == "(" or str == ")"

  def helper(tokens):
    node_name = tokens[1]
    node_args = [[]]
    tokens = tokens[2:-1] #ignore (, name, and ).

    depth = 0
    for token in tokens:
      if paren(token): 
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
open(output, 'w').write(ast.compile())
