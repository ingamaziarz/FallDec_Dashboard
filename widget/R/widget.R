# AUTO GENERATED FILE - DO NOT EDIT

#' @export
widget <- function(id=NULL, data=NULL, label=NULL, value=NULL) {
    
    props <- list(id=id, data=data, label=label, value=value)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'Widget',
        namespace = 'widget',
        propNames = c('id', 'data', 'label', 'value'),
        package = 'widget'
        )

    structure(component, class = c('dash_component', 'list'))
}
