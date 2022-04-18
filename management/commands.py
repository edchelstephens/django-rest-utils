from django.core.management.base import BaseCommand

class CustomManagementCommandMixin(BaseCommand):
    """Base mixin for Command classes for django management custom commands.
    
    https://docs.djangoproject.com/en/2.1/howto/custom-management-commands/#module-django.core.management
    """
    def write_mapping_to_stdout(self, mapping, add_newline=True):
        """Write mapping to standard output"""
        for key, value in mapping.items():
            self.stdout.write(self.style.SQL_COLTYPE("{} : {}".format(key, value)))
        
        if add_newline:
            self.stdout.write("\n")

    def write_iterable_items_to_stdout(self, iterables, style="SQL_COLTYPE", method=repr):
        """Write items of iterable using printing method"""
        if method not in (str, repr):
            raise TypeError("Callable argument method must be repr or str")

        for item in iterables:
            write_style = self.style.SQL_KEYWORD if style == "SQL_KEYWORD" else self.style.SQL_COLTYPE
            self.stdout.write(write_style(method(item)))

    def show_stdout_styles(self):
        """Write styled characters on standard output."""
        self.stdout.write(self.style.HTTP_INFO("\n#### Available styles: #### \n"))
       
        styled_text = [
            self.style.ERROR("self.style.ERROR()"),
            self.style.SUCCESS("self.style.SUCCESS()"),
            self.style.WARNING("self.style.WARNING()"),
            self.style.NOTICE("self.style.NOTICE()"),
            self.style.SQL_FIELD("self.style.SQL_FIELD()"),
            self.style.SQL_COLTYPE("self.style.SQL_COLTYPE()"),
            self.style.SQL_KEYWORD("self.style.SQL_KEYWORD()"),
            self.style.SQL_TABLE("self.style.SQL_TABLE()"),
            self.style.HTTP_INFO("self.style.HTTP_INFO()"),
            self.style.HTTP_SUCCESS("self.style.HTTP_SUCCESS()"),
            self.style.HTTP_REDIRECT("self.style.HTTP_REDIRECT()"),
            self.style.HTTP_NOT_MODIFIED("self.style.HTTP_NOT_MODIFIED()"),
            self.style.HTTP_BAD_REQUEST("self.style.HTTP_BAD_REQUEST()"),
            self.style.HTTP_NOT_FOUND("self.style.HTTP_NOT_FOUND()"),
            self.style.HTTP_SERVER_ERROR("self.style.HTTP_SERVER_ERROR()"),
            self.style.HTTP_NOT_MODIFIED("self.style.MIGRATE_HEADING()"),
            self.style.HTTP_NOT_MODIFIED("self.style.MIGRATE_LABEL()"),
        ]
        for text in styled_text:
            self.stdout.write(text)
        
        self.stdout.write(self.style.HTTP_INFO("\n>> Usage Example: self.stdout.write(self.style.HTTP_INFO('Info message'))"))
        self.stdout.write(self.style.HTTP_INFO("\n#### End styles: #### \n"))