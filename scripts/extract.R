library(Microsoft365R)
library(frictionless)
library(purrr)

extract_resource <- function(resource_name, descriptor) {
  # prevent multiple "Please make sure you have the right to access data..." on logs
  package <- suppressMessages(read_package(descriptor))
  resource <- keep(package$resources, ~ .x$name == resource_name)[[1]]
  
  # prevent multiple "Loading Microsoft Graph ..." on logs
  site <- suppressMessages(get_sharepoint_site(site_url = resource[["sharepoint"]][["path"]]))
  docs <- site$get_drive(resource[["sharepoint"]][["drive"]])
  item <- docs$get_item(resource[["sharepoint"]][["item"]])
  item$download(resource[["path"]], overwrite = TRUE)
}

main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  # resource_name <- "exec_rec"
  resource_name <- args[[1]]
  extract_resource(resource_name, descriptor = "datapackage.yaml")
}

main()
