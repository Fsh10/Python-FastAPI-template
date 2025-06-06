class BaseSchemasForRouter:
    """
        This class is made to be basic for all schemas for different models.
        Names are obvious what they should contains
        Example of use:
    ```
    class OrderSchemas(SchemasForRouter):
        def __init__(self):
            super().__init__(get_response_scheme=GetOrderScheme,
                             create_request_scheme=CreateOrderScheme,
                             update_request_scheme=UpdateOrderScheme)
    class GetOrderScheme(BaseModel):
        example_field: str
        example_field2: int
    class CreateOrderScheme(BaseModel):
        # example in GetOrderScheme
    class UpdateOrderScheme(BaseModel):
        # example in GetOrderScheme

    order_schemas = OrderSchemas() # - this object we use when make super().__init__(schemas=order_schemas)
    ```
    """

    def __init__(
        self,
        get_response_scheme=None,
        get_short_scheme=None,
        create_request_scheme=None,
        update_request_scheme=None,
    ):
        self.get_response_scheme = get_response_scheme
        self.create_request_scheme = create_request_scheme
        self.update_request_scheme = update_request_scheme
        self.get_short_scheme = get_short_scheme


def get_base_schemas() -> BaseSchemasForRouter:
    return BaseSchemasForRouter()
