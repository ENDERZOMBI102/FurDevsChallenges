from types import LambdaType
from typing import Callable, Any

WhenBody = dict[ Callable[ [ Any ], bool ], Any ]


def When( body: WhenBody, obj: Any ) -> Any:
	key: LambdaType
	for key, value in body.items():
		if len( key.__code__.co_varnames ) == 1:
			if key( obj ):
				if isinstance( value, LambdaType ):
					if len( value.__code__.co_varnames ) > 1:
						return value( **{ name: val for name, val in obj.__dict__.items() if name in value.__code__.co_varnames } )
					return value()
				return value
		else:
			if key( **{ name: val for name, val in obj.__dict__.items() if name in key.__code__.co_varnames } ):
				if isinstance( value, LambdaType ):
					if len( value.__code__.co_varnames ) > 1:
						return value( **{ name: val for name, val in obj.__dict__.items() if name in value.__code__.co_varnames } )
					return value()
				return value


# noinspection PyRedeclaration
When: Callable[ [ WhenBody, Any ], Any ] = lambda body, obj: (
	result := [ body ],
	matchDict := lambda obj1: { name: val for name, val in obj.__dict__.items() if name in obj1.__code__.co_varnames },
	execValue := lambda value: value( **matchDict( value ) ) if len( value.__code__.co_varnames ) > 1 else value(),
	execOrReturnValue := lambda value: result.__setitem__( 0, execValue( value ) ) if isinstance( value, LambdaType ) else value,
	[
		(
			(
				(
					execOrReturnValue( value ) if key( obj ) else None
				) if len( key.__code__.co_varnames ) == 1 else (
					execOrReturnValue( value ) if key( **matchDict( key ) ) else None
				)
			) if result[0] == body else None
		) for key, value in body.items()
	]
)[0][0]
