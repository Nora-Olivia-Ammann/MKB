import warnings
import re


# general call for RegEx pattern
# pattern_correct, pattern_leading_zero, pattern_dummy = regex_function
############################################

class RegExPattern:

    @staticmethod
    def general_re_pattern():
        """
        compiles and returns the general RegEx pattern for all Inventarnummern
        :return: correct pattern, leading zero pattern, dummy pattern
        """
        warnings.warn("Used Inventarnummer RegEx Pattern: General")
        # the correct pattern
        pattern_correct = re.compile(r"^\(F\)[IV]{1,3}[abcde]?\s[1-9][0-9]*[a-z]?$")
        # a pattern with a leading zero
        pattern_leading_zero = re.compile(r"^\(F\)[IV]{1,3}[abcde]?\s0+[1-9][0-9]*[a-z]?$")
        # a pattern for the dummy inventarnummer
        pattern_dummy = re.compile(r"^\(F\)[a-zA-Z]*\sDU-[0-9]+$")
        # to copy paste in code when using
        # pattern_correct, pattern_leading_zero, pattern_dummy = REPAT.general_re_pattern()
        return pattern_correct, pattern_leading_zero, pattern_dummy

    @staticmethod
    def ozeanien_re_pattern():
        """
        compiles and returns the general RegEx pattern for the Abteilung Ozeanien
        :return: correct pattern, leading zero pattern, dummy pattern
        """
        # OZEANIEN PATTERN
        warnings.warn("Used Inventarnummer RegEx Pattern: Ozeanien, Va/b/c")
        # the correct pattern
        pattern_correct = re.compile(r"^\(F\)V[abc]\s[1-9][0-9]*[a-z]?$")
        # a pattern with a leading zero
        pattern_leading_zero = re.compile(r"^\(F\)V[abc]\s0+[1-9][0-9]*[a-z]?$")
        # a pattern for the dummy inventarnummer, here the latin numerals don't have to match
        pattern_dummy = re.compile(r"^\(F\)[a-zA-Z]*\sDU-[0-9]*$")
        # to copy paste in code when using
        # pattern_correct, pattern_leading_zero, pattern_dummy = REPAT.ozeanien_re_pattern()
        return pattern_correct, pattern_leading_zero, pattern_dummy

    @staticmethod
    def inventar_sortierbar_re_pattern():
        """
        Compiles and returns patterns that are used to add a sortable Inventarnummer. These are all roughtly
        correct patterns, this is sufficient to add leading zeros to make them sortable.
        :return: pattern without a letter at the end, pattern with a letter, pattern with a letter and a blank space
        """
        # establish the pattern
        pattern_no_letter = re.compile(r"^\(F\)[a-zA-Z]+\s[0-9]*$")
        pattern_letter = re.compile(r"^\(F\)[a-zA-Z]+\s[0-9]*[a-z]+$")
        # we need to differentiate between these two as otherwise the number of leading zeros would be incorrect
        pattern_letter_blank = re.compile(r"^\(F\)[a-zA-Z]+\s[0-9]*\s[a-z]+$")
        # pattern_no_letter, pattern_letter, pattern_letter_blank = REPAT.inventar_sortierbar_re_pattern()
        return pattern_no_letter, pattern_letter, pattern_letter_blank

    @staticmethod
    def inschrift_re_pattern():
        """
        Compiles and returns RegEx pattern for the Einlaufnummer (Inschrift).
        :return: correct pattern, leading zero pattern, incomplete pattern
        """
        pattern_einlauf_correct = re.compile(r"^fot_[012][0-9]{3}$")
        # establish a pattern for numbers only containing zero
        pattern_zero = re.compile(r"^fot_0*$")
        # establish a RegEx pattern for an incomplete Einlaufnummer it must contain four digits
        # the ones that are completely false will be changed manually
        pattern_incomplete = re.compile(r"^fot_[0-9]{1,3}$")
        # to copy paste in code when using
        # pattern_einlauf_correct, pattern_zero, pattern_incomplete = REPAT.inschrift_re_pattern()
        return pattern_einlauf_correct, pattern_zero, pattern_incomplete


#####################
# TEST

# Helpful Website: https://regex101.com

lis = ["(F)VB 16670", " (F)V 123", "(F) Vb 123", "(F)Vb 01245", "(F)bs 12356 ", "(F)Vb Vb 123", "Vb 1235",
       "(F)Vb DU-0118", "(F)Vb DU-0", "(F)Vb 0", "(F)Vb DU-", "", "(F)Vc 00", "(F)Vc 001"]

leading_zero_list = ["(F)Vb 01245", "(F)Vb 0", "(F)Vc 00", "(F)Vc 001", "(F)Vc 01", "(F)Vb 00205"]

if __name__ == "__main__":
    pass
