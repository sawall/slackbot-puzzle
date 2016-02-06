# quick and dirty conversions for puzzle solving
# scott boone / sawall@github 
#
# license ref: http://creativecommons.org/licenses/by/4.0/

from slackbot.bot import respond_to
import string
import operator
import binascii
import hashlib
import base64

@respond_to('md5 (.*)')
def md5(message, thing):
    message.reply('md5: \"%s\"' % hashlib.md5(thing.encode('utf8')).hexdigest())

@respond_to('sha256 (.*)')
def sha256(message, thing):
    message.reply('sha256: \"%s\"' % hashlib.sha256(thing.encode('utf8')).hexdigest())

@respond_to('ascii2hex (.*)')
def ascii2hex(message, thing):
    message.reply('hex: \"%s\"' % binascii.hexlify(thing.encode('utf8')))

@respond_to('hex2int (.*)')
def hex2int(message, thing):
    message.reply('int: \"%d\"' % int(thing,16))

@respond_to('ascii2b64 (.*)')
def ascii2b64(message, thing):
    message.reply('base64: \"%s\"' % base64.b64encode(thing.encode('utf8')))

@respond_to('b642ascii (.*)')
def b642ascii(message, thing):
    message.reply('ascii: \"%s\"' % binascii.a2b_base64(thing))

@respond_to('reverse (.*)')
def reverse(message, thing):
    message.reply('reversed: \"%s\"' % thing[::-1])

# TODO: frontend pycrypto: https://www.dlitz.net/software/pycrypto/doc/#crypto-cipher-encryption-algorithms
# TODO: bin to hex
# TODO: hex to bin
