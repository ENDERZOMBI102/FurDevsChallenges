from __future__ import annotations

from pathlib import Path

import wx


assets = Path( __file__ ).parent / 'assets'


# https://opengameart.org/content/chess-pieces-and-board-squares


class Piece(wx.DragImage):

	def __init__( self ) -> None:
		super().__init__( wx.Bitmap( str( assets / 'b_bishop.png' ) ) )


class BoardCell(wx.Control):
	lightCell: bool
	cellBitmap: wx.Bitmap
	overlayBrush: wx.Brush
	highlighted: bool = False
	piece: Piece | None = None

	def __init__( self, parent: wx.Window, x: int, y: int, light: bool, bitmap: wx.Bitmap ) -> None:
		super().__init__(
			parent=parent,
			size=wx.Size( 80, 80 ),
			pos=wx.Point( x * 80, y * 80 ),
			name=f'{x}_{y}_{light}'
		)
		self.lightCell = light
		self.cellBitmap = bitmap
		self.piece = Piece()
		self.overlayBrush = wx.Brush()
		self.overlayBrush.SetColour( wx.Colour( red=0, green=0, blue=255, alpha=1 ) )

		self.Bind( wx.EVT_ENTER_WINDOW, self.onMouseEnter, self )
		self.Bind( wx.EVT_LEAVE_WINDOW, self.onMouseLeave, self )

	def onMouseEnter( self, evt: wx.MouseEvent ) -> None:
		self.highlighted = True

	def onMouseLeave( self, evt: wx.MouseEvent ) -> None:
		self.highlighted = False

	def onDraw( self ) -> None:
		self.piece.Move( wx.MouseState().GetPosition() )
		dc = wx.ClientDC( self )
		dc.DrawBitmap( self.cellBitmap, self.GetPosition() )
		if self.highlighted:
			dc.SetBrush( self.overlayBrush )
			dc.DrawRectangle( rect=self.GetRect() )


class Root(wx.Frame):
	lightCellBitmap: wx.Bitmap
	darkCellBitmap: wx.Bitmap
	board: list[ list[ BoardCell ] ]

	def __init__( self ) -> None:
		super().__init__(
			parent=None,
			size=wx.Size( 80 * 8 + 16, 80 * 8 + 39 ),  # mmm, yes, who doesn't love magic constants
			style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX
		)
		self.CenterOnScreen()
		self.SetTitle('ChessLiner')

		self.timer = wx.Timer( self )
		self.lightCellBitmap = wx.Bitmap( str( assets / 'square_gray_light.png' ) ).ConvertToImage().Rescale( 80, 80 ).ConvertToBitmap()
		self.darkCellBitmap = wx.Bitmap( str( assets / 'square_gray_dark.png' ) ).ConvertToImage().Rescale( 80, 80 ).ConvertToBitmap()

		lightCell = True
		self.board = [ [], [], [], [], [], [], [], [] ]
		for y in range( 8 ):
			for x in range( 8 ):
				self.board[y] += [
					BoardCell( self, x, y, lightCell, self.lightCellBitmap if lightCell else self.darkCellBitmap )
				]
				lightCell = not lightCell
			lightCell = not lightCell

		self.Bind( wx.EVT_CLOSE, self.onClose, self )
		self.Bind( wx.EVT_TIMER, self.draw )

		self.timer.Start( 20 )

	def onClose( self, evt: wx.CommandEvent ) -> None:
		self.timer.Stop()
		evt.Skip()

	def draw( self, evt: wx.TimerEvent ) -> None:
		dc = wx.ClientDC(self)
		for row in self.board:
			for cell in row:
				cell.onDraw()


if __name__ == '__main__':
	app = wx.App()
	wx.InitAllImageHandlers()
	root = Root()
	root.Show()
	app.SetTopWindow( root )
	app.SetExitOnFrameDelete(True)
	app.MainLoop()
