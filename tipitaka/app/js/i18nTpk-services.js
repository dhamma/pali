'use strict';

/* Services */


angular.module('paliTipitaka.i18nTpk', ['pali.data.i18nTpk']).
  factory('i18nTpkConvert', ['$location', 'i18nTpk', function($location, i18nTpk) {
    function endswith(str, suffix) {
      return str.indexOf(suffix, str.length - suffix.length) != -1;
    }

    function nodeTextStrip(text) {
      // remove leading and trailing un-needed characters
      return text.replace(/^[\d\s()-\.]+/, '').replace(/-\d$/, '');
    }

    function nodeTextStrip2(text) {
      var str = nodeTextStrip(text); 
      if (endswith(str, 'pāḷi'))
        return str.slice(0, -4);
      if (endswith(str, 'nikāya'))
        return str.slice(0, -6);
      if (endswith(str, 'piṭaka'))
        return str.slice(0, -6);
      if (endswith(str, 'piṭaka (aṭṭhakathā)'))
        return str.slice(0, -19);
      if (endswith(str, '-aṭṭhakathā')) {
        if (endswith(str, 'kaṇḍa-aṭṭhakathā'))
          return str.slice(0, -16);
        else
          return str.slice(0, -11);
      }
      if (endswith(str, 'nikāya (aṭṭhakathā)')) {
        if (endswith(str, ' nikāya (aṭṭhakathā)'))
          return str.slice(0, -20);
        else
          return str.slice(0, -19);
      }
      if (endswith(str, 'piṭaka (ṭīkā)'))
        return str.slice(0, -13);
      if (endswith(str, 'nikāya (ṭīkā)'))
        return str.slice(0, -13);
      if (endswith(str, '-mūlaṭīkā'))
        return str.slice(0, -9);
      if (endswith(str, '-ṭīkā'))
        return str.slice(0, -5);
      return str;
    }

    function gettextCanonName(name, locale) {
      if (i18nTpk.canonTextTranslation.hasOwnProperty(locale)) {
        if (i18nTpk.canonTextTranslation[locale].hasOwnProperty(name)) {
          return i18nTpk.canonTextTranslation[locale][name];
        }
      }
      return name;
    }

    function gettextFuzzyCanonName(name, locale) {
      var trName = gettextCanonName(name, locale);
      if (trName !== name)
        return trName;
      trName = gettextCanonName(name + 'pāḷi', locale);
      if (trName !== (name + 'pāḷi'))
        return trName;
      return name;
    }

    function translateNodeText(text, locale) {
      var str = nodeTextStrip(text);
      var trText = gettextCanonName(str, locale)
      if (trText == str) {
        if (endswith(trText, ' (aṭṭhakathā)')) {
          return gettextCanonName(text.slice(0, -13), locale) + ' ' +
                 gettextCanonName('Aṭṭhakathā', locale);
        }
        if (endswith(trText, '-aṭṭhakathā')) {
          return gettextFuzzyCanonName(text.slice(0, -11), locale) + ' ' +
                 gettextCanonName('Aṭṭhakathā', locale);
        }
        if (endswith(trText, ' (ṭīkā)')) {
          return gettextCanonName(text.slice(0, -7), locale) + ' ' +
                 gettextCanonName('Tīkā', locale);
        }
        if (endswith(trText, '-ṭīkā')) {
          return gettextFuzzyCanonName(text.slice(0, -5), locale) + ' ' +
                 gettextCanonName('Tīkā', locale);
        }
        return text;
      }
      return trText;
    }

    function translateNodeText2(text, locale) {
      var str = nodeTextStrip(text);
      var trStr = translateNodeText(text, locale);
      if (trStr === text)
        return text;
      else
        return text.replace(str, trStr);
    }

    function translateNodeText3(text, locale) {
      var trStr = translateNodeText(text, locale);
      if (trStr === text)
        return '';
      else
        return ' (' + trStr + ')';
    }

    function redirectAccordingToUrlLocale(path) {
      if ($location.path().indexOf('/en_US/') === 0) {
        $location.path('/en_US' + path);
      } else if ($location.path().indexOf('/zh_TW/') === 0) {
        $location.path('/zh_TW' + path);
      } else if ($location.path().indexOf('/zh_CN/') === 0) {
        $location.path('/zh_CN' + path);
      } else {
        $location.path(path);
      }
    }

    var serviceInstance = {
      nodeTextStrip2: nodeTextStrip2,
      translateNodeText: translateNodeText,
      translateNodeText2: translateNodeText2,
      translateNodeText3: translateNodeText3,
      redirectAccordingToUrlLocale: redirectAccordingToUrlLocale
    };
    return serviceInstance;
  }]);
