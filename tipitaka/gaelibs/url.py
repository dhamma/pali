#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, json
from google.appengine.api import urlfetch
from lxml import etree
import xml.dom.minidom

with open(os.path.join(os.path.dirname(__file__), '../common/gae/libs/json/treeviewAll.json'), 'r') as f:
  treeviewData = json.loads(f.read())

result = urlfetch.fetch('http://1.epalitipitaka.appspot.com/romn/cscd/tipitaka-latn.xsl')
if result.status_code == 200:
  xslt_root = etree.fromstring(result.content)
  transform = etree.XSLT(xslt_root)
else:
  raise Exception('cannot fetch http://1.epalitipitaka.appspot.com/romn/cscd/tipitaka-latn.xsl')


translationInfo = {
  'zh_TW': {
    'canon': {
      's0502m.mul0.xml': ['2'],
      's0502m.mul1.xml': ['2'],
      's0502m.mul2.xml': ['2'],
      's0502m.mul3.xml': ['2'],
      's0502m.mul4.xml': ['2'],
      's0505m.mul0.xml': ['1']
    },
    'source': {
      '1': ['郭良鋆', 'http://blog.yam.com/benji/article/34665984'],
      '2': ['了參法師(葉均)', 'http://myweb.ncku.edu.tw/~lsn46/Tipitaka/Sutta/Khuddaka/Dhammapada/ven-l-z-all.htm'],
      '3': ['蕭式球', 'http://www.chilin.edu.hk/edu/report_section.asp?section_id=5']
    }
  },
  'en_US': {
    'canon': {
      's0502m.mul0.xml': ['1'],
      's0502m.mul1.xml': ['1'],
      's0502m.mul2.xml': ['1'],
      's0502m.mul3.xml': ['1'],
      's0502m.mul4.xml': ['1']
    },
    'source': {
      '1': ['Ṭhānissaro Bhikkhu', 'http://www.accesstoinsight.org/tipitaka/translators.html#than', 'http://www.accesstoinsight.org/lib/authors/thanissaro/dhammapada.pdf']
    }
  }
}

canonName = {
  's0505m.mul0.xml': {
    'pali': 'Suttanipāta, Uragavaggo',
    'zh_TW': '經集, 蛇品'
  },
  's0502m.mul0.xml': {
    'pali': 'Dhammapada, Yamakavaggo',
    'en_US': 'Dhammapada, Pairs',
    'zh_TW': '法句, 雙品'
  },
  's0502m.mul1.xml': {
    'pali': 'Dhammapada, Appamādavaggo',
    'en_US': 'Dhammapada, Heedfulness',
    'zh_TW': '法句, 不放逸品'
  },
  's0502m.mul2.xml': {
    'pali': 'Dhammapada, Cittavaggo',
    'en_US': 'Dhammapada, The Mind',
    'zh_TW': '法句, 心品'
  },
  's0502m.mul3.xml': {
    'pali': 'Dhammapada, Pupphavaggo',
    'en_US': 'Dhammapada, Blossoms',
    'zh_TW': '法句, 華(花)品'
  },
  's0502m.mul4.xml': {
    'pali': 'Dhammapada, Bālavaggo',
    'en_US': 'Dhammapada, Fools',
    'zh_TW': '法句, 愚品'
  }
}


def getHtmlTitle(userLocale, reqHandlerName, i18n):
  return ''


def recursivelyCheck(node, path):
  if path[0] is None:
    # check if all items are None
    for subPath in path:
      if subPath is not None:
        return False
    # all items are None => True
    return True

  else:
    for child in node['child']:
      if path[0].decode('utf-8') == child['url']:
        if 'action' in child:
          # check if all remaining items are None
          for subPath in path[1:]:
            if subPath is not None:
              return False
          # all remaining items are None => True
          return True
        else:
          return recursivelyCheck(child, path[1:])

    return False


def isValidCanonPath(path1, path2, path3, path4, path5):
  # rootNode is tipitaka, no commentaris and sub-commentaries
  rootNode = treeviewData['child'][0]
  path = [path1, path2, path3, path4, path5]

  return recursivelyCheck(rootNode, path)


def getCanonPageHtml(urlLocale, path1, path2, path3, path4, path5, reqPath):
  # before using this funtion, make sure to call 'isValidCanonPath' first

  # rootNode is tipitaka, no commentaris and sub-commentaries
  rootNode = treeviewData['child'][0]
  path = [path1, path2, path3, path4, path5]

  isFinished = False
  node = rootNode
  count = 0
  # find the node which contains necessary information to build html
  while True:
    if path[0] is None:
      isFinished = True
    else:
      for child in node['child']:
        if path[0].decode('utf-8') == child['url']:
          if 'action' in child:
            isFinished = True
          node = child
          path = path[1:]
          break

    count += 1
    if count > 5:
      raise Exception('getCanonPageHtml: loop count too much')
    if isFinished:
      break

  # the node we need is found. Start to build html
  html = u''
  if 'action' in node:
    # fetch xml
    xmlUrl = 'http://1.epalitipitaka.appspot.com/romn/%s' % node['action']
    result = urlfetch.fetch(xmlUrl)
    if result.status_code == 200:
      # successfully fetch xml
      root = etree.fromstring(result.content)
      # transform xml with xslt
      root = transform(root)
      # feed transformed data to minidom for processing
      dom = xml.dom.minidom.parseString(etree.tostring(root))
      # return only innerHTML of body
      html += dom.documentElement.getElementsByTagName('body')[0].toxml()[6:-7]
    else:
      # fail to fetch xml
      raise Exception('cannot fetch %s' % xmlUrl)
  else:
    for child in node['child']:
      html += u'<a href="%s/%s">%s</a>' % (reqPath, child['url'], child['text'])

  return html


def recursivelyCheck2(node, path):
  for child in node['child']:
    if path[0].decode('utf-8') == child['url']:
      if 'action' in child:
        # check if all remaining items are None
        for subPath in path[1:]:
          if subPath is not None:
            return {'isValid': False }
        # all remaining items are None => True
        return {'isValid': True, 'node': child }
      else:
        if len(path) == 1:
          return {'isValid': False }
        elif path[1] is None:
          return {'isValid': False }
        else:
          return recursivelyCheck2(child, path[1:])

  return {'isValid': False }


def isValidTranslationOrContrastReadingPage(path1, path2, path3, path4, path5, locale, translator):
  # rootNode is tipitaka, no commentaris and sub-commentaries
  rootNode = treeviewData['child'][0]
  path = [path1, path2, path3, path4, path5]

  result = recursivelyCheck2(rootNode, path)
  if result['isValid']:
    if locale in translationInfo:
      xmlFilename = os.path.basename(result['node']['action'])
      if xmlFilename in translationInfo[locale]['canon']:
        for translatorCode in translationInfo[locale]['canon'][xmlFilename]:
          if translationInfo[locale]['source'][translatorCode][0] == translator:
            return {'isValid': True, 'node': result['node'] }
        return {'isValid': False }
      else:
        return {'isValid': False }
    else:
      return {'isValid': False }
  else:
    return {'isValid': False }


def getTranslationPageHtml(locale, translator, node):
  if 'action' not in node:
    raise Exception('In getTranslationPageHtml: action attribute not in node!')

  html = u''

  # fetch xml
  xmlFilename = os.path.basename(node['action'])
  if xmlFilename in translationInfo[locale]['canon']:
    for translatorCode in translationInfo[locale]['canon'][xmlFilename]:
      if translationInfo[locale]['source'][translatorCode][0] == translator:
        code = translatorCode
        break
    if code is None:
      raise Exception('cannot find translatorCode')
  else:
    raise Exception("%s not in translationInfo[%s]['canon']" % (xmlFilename, locale))

  xmlUrl = 'http://1.epalitipitaka.appspot.com/translation/%s/%s/%s' % (locale, code, xmlFilename)
  result = urlfetch.fetch(xmlUrl)
  if result.status_code == 200:
    # successfully fetch xml
    root = etree.fromstring(result.content)
    # transform xml with xslt
    root = transform(root)
    # feed transformed data to minidom for processing
    dom = xml.dom.minidom.parseString(etree.tostring(root))
    # return only innerHTML of body
    html += dom.documentElement.getElementsByTagName('body')[0].toxml()[6:-7]
  else:
    # fail to fetch xml
    raise Exception('cannot fetch %s' % xmlUrl)

  return html


if __name__ == '__main__':
  # for test purpose
  if isValidCanonPath(None, None, None, None, None) is not True:
    print('test failure:')
    print('isValidCanonPath(None, None, None, None, None) is not True')

  if isValidCanonPath(None, None, None, None, '123') is not False:
    print('test failure:')
    print("isValidCanonPath(None, None, None, None, '123') is not False")

  if isValidCanonPath('sutta', 'dīgha', 'sīlakkhandhavagga', 'kūṭadantasuttaṃ', None) is not True:
    print('test failure:')
    print("isValidCanonPath('sutta', 'dīgha', 'sīlakkhandhavagga', 'kūṭadantasuttaṃ', None) is not True")

  if isValidCanonPath('abhidhamma', 'kathāvatthu', 'puggalakathā', None, None) is not True:
    print('test failure:')
    print("isValidCanonPath('abhidhamma', 'kathāvatthu', 'puggalakathā', None, None) is not True")

  if isValidCanonPath('sutta', 'dīgha', None, None, None) is not True:
    print('test failure:')
    print("isValidCanonPath('sutta', 'dīgha', None, None, None) is not True")

  if isValidCanonPath('sutta', None, None, None, None) is not True:
    print('test failure:')
    print("isValidCanonPath('sutta', None, None, None, None) is not True")

  if isValidCanonPath('sutta1', None, None, None, None) is not False:
    print('test failure:')
    print("isValidCanonPath('sutta', None, None, None, None) is not False")

  if isValidCanonPath('abhidhamma', 'kathāvatthu2', 'puggalakathā', None, None) is not False:
    print('test failure:')
    print("isValidCanonPath('abhidhamma', 'kathāvatthu2', 'puggalakathā', None, None) is not False")

  print(getCanonPageHtml(None, 'sutta', 'dīgha', None, None, None, u'/canon/sutta/dīgha'))
  print(getCanonPageHtml(None, 'sutta', 'dīgha', 'sīlakkhandhavagga', None, None, u'/canon/sutta/dīgha/sīlakkhandhavagga'))
  print(getCanonPageHtml(None, 'sutta', 'dīgha', 'sīlakkhandhavagga', 'kūṭadantasuttaṃ', None, u'/canon/sutta/dīgha/sīlakkhandhavagga/kūṭadantasuttaṃ'))
  print(getCanonPageHtml(None, 'abhidhamma', 'kathāvatthu', 'puggalakathā', None, None, u'/canon/abhidhamma/kathāvatthu/puggalakathā'))
